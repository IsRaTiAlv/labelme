import torch

from torch import nn
from utils.kobiutils import get_upsampling_weight


class _CBNReLU(nn.Module):
    """Convolution plus Batchnorm and Relu"""

    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=0, bias=False):
        super(_CBNReLU, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, bias=bias),
            nn.BatchNorm2d(out_channels), nn.ReLU(True))

    def forward(self, x):
        return self.conv(x)


class _DSConv(nn.Module):
    """Depthwise Separable Convolutions"""

    def __init__(self, in_channels, out_channels, stride=1, bias=False):
        super(_DSConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels,
                      in_channels,
                      kernel_size=3,
                      stride=stride,
                      padding=1,
                      groups=in_channels,
                      bias=bias), nn.BatchNorm2d(in_channels), nn.ReLU(True),
            nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=bias),
            nn.BatchNorm2d(out_channels), nn.ReLU(True))

    def forward(self, x):
        return self.conv(x)


class _DWConv(nn.Module):
    """Depthwise Convolutions"""

    def __init__(self, in_channels, out_channels, stride=1):
        super(_DWConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels,
                      out_channels,
                      kernel_size=3,
                      stride=stride,
                      padding=1,
                      groups=in_channels,
                      bias=False), nn.BatchNorm2d(out_channels), nn.ReLU(True))

    def forward(self, x):
        return self.conv(x)


class _LinearBottleneck(nn.Module):

    def __init__(self, in_channels, out_channels, expansion=6, stride=2):
        super(_LinearBottleneck, self).__init__()
        self.shortcut = stride == 1 and in_channels == out_channels
        self.bottle = nn.Sequential(
            _CBNReLU(in_channels, in_channels * expansion, kernel_size=1),
            _DWConv(in_channels * expansion, in_channels * expansion, stride=stride),
            nn.Conv2d(in_channels * expansion, out_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(out_channels))

    def forward(self, x):
        out = self.bottle(x)
        if self.shortcut:
            out = x + out
        return out


class _PyramidPooling(nn.Module):

    def __init__(self, in_channels, out_channels):
        super(_PyramidPooling, self).__init__()
        scale_factor = int(in_channels / 4)
        self.conv0 = _CBNReLU(in_channels, scale_factor, kernel_size=1)
        self.conv1 = _CBNReLU(in_channels, scale_factor, kernel_size=1)
        self.conv2 = _CBNReLU(in_channels, scale_factor, kernel_size=1)
        self.conv3 = _CBNReLU(in_channels, scale_factor, kernel_size=1)
        self.conv4 = _CBNReLU(in_channels * 2, out_channels, kernel_size=1)

    def pool(self, x, size):
        avgpool = nn.AdaptiveAvgPool2d(size)
        return avgpool(x)

    def upsample(self, x, size):
        return nn.functional.interpolate(x, size, mode='nearest')  #, align_corners=False

    def forward(self, x):
        feat1 = self.upsample(self.conv0(self.pool(x, 1)), (30, 45))
        feat2 = self.upsample(self.conv1(self.pool(x, 3)), (30, 45))
        feat3 = self.upsample(self.conv2(self.pool(x, 5)), (30, 45))
        feat4 = self.upsample(self.conv3(self.pool(x, 15)), (30, 45))
        x = torch.cat([x, feat1, feat2, feat3, feat4], dim=1)
        x = self.conv4(x)
        return x


class FSCNN(nn.Module):

    def __init__(self, num_classes=20):
        super(FSCNN, self).__init__()
        ############################################################
        ###                          Downsample                  ###
        ############################################################
        self.ds_conv0 = _CBNReLU(3, 32, 3, 2)
        self.ds_conv1 = _DSConv(32, 48, 2)
        self.ds_conv2 = _DSConv(48, 64, 2)
        ############################################################
        ###             Global Feature Extractor                 ###
        ############################################################
        self.gfs_bottle0 = nn.Sequential(_LinearBottleneck(64, 64, expansion=6, stride=2),
                                         _LinearBottleneck(64, 64, expansion=6, stride=1),
                                         _LinearBottleneck(64, 64, expansion=6, stride=1))
        self.gfs_bottle1 = nn.Sequential(_LinearBottleneck(64, 96, expansion=6, stride=1),
                                         _LinearBottleneck(96, 96, expansion=6, stride=1),
                                         _LinearBottleneck(96, 96, expansion=6, stride=1))
        self.gfs_bottle2 = nn.Sequential(_LinearBottleneck(96, 128, expansion=6, stride=1),
                                         _LinearBottleneck(128, 128, expansion=6, stride=1),
                                         _LinearBottleneck(128, 128, expansion=6, stride=1))
        self.gfs_ppm = _PyramidPooling(128, 128)
        ############################################################
        ###                  Feature Fusion                      ###
        ############################################################
        self.ff_conv0 = _DWConv(128, 128, stride=1)
        self.ff_convLow = nn.Sequential(nn.Conv2d(in_channels=128, out_channels=128, kernel_size=1),
                                        nn.BatchNorm2d(128))
        self.ff_convHigh = nn.Sequential(nn.Conv2d(in_channels=64, out_channels=128, kernel_size=1),
                                         nn.BatchNorm2d(128))
        self.ff_relu = nn.ReLU(True)
        ############################################################
        ###                    Classifier                        ###
        ############################################################
        self.cla_conv0 = _DSConv(in_channels=128, out_channels=128, stride=1)
        self.cla_conv1 = _DSConv(in_channels=128, out_channels=128, stride=1)
        self.cla_conv2 = nn.Sequential(
            nn.Dropout(0.1), nn.Conv2d(in_channels=128, out_channels=num_classes, kernel_size=1))
        self.deconv = nn.ConvTranspose2d(num_classes,
                                         num_classes,
                                         kernel_size=16,
                                         stride=8,
                                         padding=4,
                                         bias=False)
        self.deconv.weight.data.copy_(get_upsampling_weight(num_classes, num_classes, 16))

    def forward(self, x):
        features = self.ds_conv0(x)
        features = self.ds_conv1(features)
        features = self.ds_conv2(features)
        x = self.gfs_bottle0(features)
        x = self.gfs_bottle1(x)
        x = self.gfs_bottle2(x)
        x = self.gfs_ppm(x)
        low = nn.functional.interpolate(x, size=(60, 90), mode='nearest')  #, align_corners=False
        low = self.ff_conv0(low)
        low = self.ff_convLow(low)
        high = self.ff_convHigh(features)
        x = high + low
        x = self.ff_relu(x)
        x = self.cla_conv0(x)
        x = self.cla_conv1(x)
        x = self.cla_conv2(x)
        x = self.deconv(x)
        return x


def main():
    fscnn = FSCNN(num_classes=20)
    print(fscnn)


if __name__ == "__main__":
    main()
