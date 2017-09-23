# coding=utf8
"""Functions to test tec.rinex.ObsFileV3 class."""
from collections import namedtuple
from datetime import datetime, timedelta
from io import StringIO

import pytest

from gnss_tec.rinex import ObsFileV3

AJAC_RNX = '''\
     3.02           OBSERVATION DATA    M                   RINEX VERSION / TYPE
Converto v3.4.8     IGN-RGP             20170627 013115 UTC PGM / RUN BY / DATE
AJAC                                                        MARKER NAME
10077M005                                                   MARKER NUMBER
Automatic           Institut Geographique National          OBSERVER / AGENCY
1830139             LEICA GR25          4.02                REC # / TYPE / VERS
4611118324          TRM57971.00     NONE                    ANT # / TYPE
  4696989.7040   723994.2090  4239678.3140                  APPROX POSITION XYZ
        0.0000        0.0000        0.0000                  ANTENNA: DELTA H/E/N
G   12 C1C L1C D1C S1C C2W L2W D2W S2W C5Q L5Q D5Q S5Q      SYS / # / OBS TYPES
R    8 C1C L1C D1C S1C C2P L2P D2P S2P                      SYS / # / OBS TYPES
E   16 C1C L1C D1C S1C C5Q L5Q D5Q S5Q C7Q L7Q D7Q S7Q C8Q  SYS / # / OBS TYPES
       L8Q D8Q S8Q                                          SYS / # / OBS TYPES
C    8 C1I L1I D1I S1I C7I L7I D7I S7I                      SYS / # / OBS TYPES
S    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES
DBHZ                                                        SIGNAL STRENGTH UNIT
    30.000                                                  INTERVAL
  2017    06    26    00    00    0.0000000     GPS         TIME OF FIRST OBS
  2017    06    26    23    59   30.0000000     GPS         TIME OF LAST OBS
     0                                                      RCV CLOCK OFFS APPL
G L2S -0.25000                                              SYS / PHASE SHIFT
G L2X -0.25000                                              SYS / PHASE SHIFT
R L2P  0.25000                                              SYS / PHASE SHIFT
E L8Q -0.25000                                              SYS / PHASE SHIFT
 24 R01  1 R02 -4 R03  5 R04  6 R05  1 R06 -4 R07  5 R08  6 GLONASS SLOT / FRQ #
    R09 -2 R10 -7 R11  0 R12 -1 R13 -2 R14 -7 R15  0 R16 -1 GLONASS SLOT / FRQ #
    R17  4 R18 -3 R19  3 R20  2 R21  4 R22 -3 R23  3 R24  2 GLONASS SLOT / FRQ #
 C1C  -71.940 C1P  -71.940 C2C  -71.940 C2P  -71.940        GLONASS COD/PHS/BIS
    18    18  1929     7                                    LEAP SECONDS
                                                            END OF HEADER
> 2017 06 26 00 00  0.0000000  0  4
G06  20835332.939   109490435.32508      -587.633          50.500    20835328.717    85317207.80808      -457.896          48.250    20835330.401    81762343.64108      -438.821          52.350
R04  24135247.881   129243249.65706     -2964.509          39.250    24135244.262   100522446.54306     -2305.728          39.000
E02  25206580.771   132461485.07148      1704.855          50.900    25206579.417    98916045.45308      1273.096          50.150    25206576.244   101496450.89908      1306.281          51.950    25206577.942   100206247.02308      1289.659          48.650
C10  38625935.135   201135401.51606       436.003          40.600    38625926.793   155530626.32107       337.087          45.300
>                              4  1
                                                                         COMMENT
> 2017 06 26 00 00 30.0000000  0  5
G02  23269584.628   122282497.09607      2373.850          45.900    23269574.831    95285049.78406      1849.752          40.000
R06  20254437.775   108081579.18807      1594.895          44.050    20254434.977    84063449.71306      1240.474          41.000
E03  26199562.760   137679722.61448     -1953.987          49.350    26199562.201   102812831.22108     -1459.200          48.450    26199559.507   105494888.18008     -1497.248          50.800    26199561.223   104153862.04807     -1478.202          46.700
C05  39875325.769   207641286.35906         2.988          37.750    39875315.615   160561383.77107         2.041          43.350
S20  38144728.445   200451840.25607       -84.098          44.000
'''
AGGO_RNX = '''\
     3.03           OBSERVATION DATA    G (GPS)             RINEX VERSION / TYPE
  2765121.7437 -4449247.3040 -3626403.9138                  APPROX POSITION XYZ
G   18 C1C C1W C2L C2W C5Q D1C D2L D2W D5Q L1C L2L L2W L5Q  SYS / # / OBS TYPES
       S1C S1W S2L S2W S5Q                                  SYS / # / OBS TYPES
    30.000                                                  INTERVAL
  2017     7     6     0     0    0.0000000     GPS         TIME OF FIRST OBS
  2017     7     6    23    59   30.0000000     GPS         TIME OF LAST OBS
                                                            END OF HEADER
> 2017 07 06 00 00 00.0000000  0 10
G01  25872596.694 5                                                  25872598.573 5      -835.376 5                                      -623.975 5 135961420.07105                                 101529641.32405        31.502                                                          34.695
G06  24373864.719 7  24373864.469 4  24373867.018 6  24373866.634 4  24373867.324 7      2722.126 7      2121.084 6      2121.135 4      2032.803 7 128085548.36107  99806924.44506  99806902.43404  95648294.08907        43.469          29.289          40.946          29.289          43.632
G12  23009061.738 7  23009061.649 5  23009060.325 6  23009059.563 5                      2101.092 7      1637.319 6      1637.210 5                 120913432.63107  94218264.09906  94218259.11005                        46.537          32.036          38.504          32.036
G13  21120555.857 8  21120555.553 6                  21120554.266 6                     -2112.487 8                     -1646.091 6                 110989301.38308                  86485166.43406                        49.245          38.778                          38.778
G15  21281254.044 8  21281254.057 6  21281252.727 7  21281252.489 6                        69.499 8        54.105 7        54.157 6                 111833765.57908  87143198.59907  87143185.59806                        50.827          40.560          44.600          40.560
G17  20941148.214 8  20941148.045 6  20941146.380 7  20941146.405 6                     -1305.397 8     -1017.184 7     -1017.186 6                 110046540.72808  85750547.86907  85750574.87306                        51.347          41.030          44.715          41.030
G19  21014348.084 7  21014347.132 6                  21014344.732 6                       269.506 7                       210.005 6                 110431222.87607                  86050300.59306                        47.747          40.400                          40.400
G24  22510822.979 7  22510823.028 5  22510824.122 7  22510824.133 5  22510825.017 8      2697.243 7      2101.726 7      2101.750 5      2014.141 8 118295181.64007  92178065.91507  92178064.90105  88337331.65608        43.371          33.970          44.546          33.970          50.358
G28  23425307.546 7  23425306.831 4                  23425305.635 4                     -3199.028 7                     -2492.749 4                 123100897.07907                  95922795.56504                        43.113          25.519                          25.519
G30  24576832.067 7  24576831.280 4  24576834.074 6  24576834.357 4  24576834.935 7     -2759.739 7     -2150.604 6     -2150.451 4     -2060.839 7 129152156.28207 100638067.50306 100638061.51204  96444807.29807        43.467          25.083          37.947          25.083          43.410
> 2017 07 06 00 00 30.0000000  0 10
G01  25877411.255 5  25877410.705 1  25877413.578 4  25877412.663 1  25877413.367 6      -851.207 5      -663.303 4      -663.274 1      -635.773 6 135986722.80605 105963683.03104 105963674.99001 101548536.27506        30.830           7.875          28.123           7.875          37.936
G06  24358326.793 7  24358326.615 4  24358328.603 6  24358330.598 4  24358330.489 7      2721.141 7      2120.353 6      2120.369 4      2032.011 7 128003899.04807  99743301.60406  99743279.62304  95587322.21707        43.625          28.360          40.739          28.360          45.252
G12  22997085.783 7  22997085.739 5  22997083.860 6  22997082.917 5                      2094.585 7      1632.139 6      1632.144 5                 120850498.10307  94169224.25006  94169219.24505                        47.488          32.365          38.171          32.365
G13  21132660.840 8  21132660.532 6                  21132659.517 6                     -2128.277 8                     -1658.396 6                 111052914.38608                  86534735.00406                        49.208          38.547                          38.547
G15  21280913.544 8  21280913.552 6  21280912.143 7  21280911.912 6                        49.858 8        38.941 7        38.854 6                 111831976.41508  87141804.42707  87141791.44706                        50.847          40.594          44.591          40.594
G17  20948658.979 8  20948658.778 6  20948657.084 7  20948656.974 6                     -1325.727 8     -1033.037 7     -1033.032 6                 110086008.81608  85781302.22807  85781329.23606                        51.289          40.970          44.825          40.970
G19  21012862.552 7  21012861.587 6                  21012858.959 6                       250.904 7                       195.508 6                 110423415.66607                  86044217.06006                        47.309          40.672                          40.672
G24  22495433.975 7  22495434.059 5  22495434.757 7  22495434.923 5  22495436.054 8      2694.044 7      2099.375 7      2099.256 5      2011.864 8 118214310.98107  92115049.82607  92115048.82905  88276941.24008        45.482          34.890          43.809          34.890          50.768
G28  23443572.146 6  23443571.480 4                  23443569.865 4                     -3199.458 6                     -2493.081 4                 123196875.12506                  95997583.64104                        41.359          24.421                          24.421
G30  24592601.178 7  24592600.441 4  24592601.649 6  24592602.519 4  24592603.253 7     -2764.328 7     -2153.929 6     -2154.031 4     -2064.341 7 129235017.47207 100702634.64606 100702628.65404  96506684.15607        44.358          25.429          37.119          25.429          44.175
'''
HKWS_HEADER = '''\
     3.02           OBSERVATION DATA    M: MIXED            RINEX VERSION / TYPE
G   16 C1C L1C D1C S1C C2S L2S D2S S2S C2W L2W D2W S2W C5Q  SYS / # / OBS TYPES
       L5Q D5Q S5Q                                          SYS / # / OBS TYPES
R   12 C1C L1C D1C S1C C2P L2P D2P S2P C2C L2C D2C S2C      SYS / # / OBS TYPES
E   16 C1C L1C D1C S1C C5Q L5Q D5Q S5Q C7Q L7Q D7Q S7Q C8Q  SYS / # / OBS TYPES
       L8Q D8Q S8Q                                          SYS / # / OBS TYPES
C    8 C1I L1I D1I S1I C7I L7I D7I S7I                      SYS / # / OBS TYPES
J   12 C1C L1C D1C S1C C2S L2S D2S S2S C5Q L5Q D5Q S5Q      SYS / # / OBS TYPES
S    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES
    30.000                                                  INTERVAL
  2015    12    19    00    00    0.0000000     GPS         TIME OF FIRST OBS
  2015    12    19    23    59   30.0000000     GPS         TIME OF LAST OBS
                                                            END OF HEADER
'''


@pytest.fixture()
def dumb_obs():
    obs_file = StringIO(HKWS_HEADER)

    return ObsFileV3(
        obs_file,
        version=3.02,
    )


@pytest.fixture
def obs():
    obs_file = StringIO(AJAC_RNX)
    glo_frq = {
        4: {datetime(2017, 6, 26, 0): 6},
        6: {datetime(2017, 6, 26, 0): -4},
    }
    return ObsFileV3(
        obs_file,
        version=3.02,
        glo_freq_nums=glo_frq,
    )


@pytest.fixture
def attr_obs():
    obs_file = StringIO(AGGO_RNX)
    priority = {
        'G': {
            1: ('P', 'C'),
            2: ('W', 'C'),
            5: ('I', 'Q', 'X'),
        }
    }
    return ObsFileV3(
        obs_file,
        version=3.03,
        obs_channel_priority=priority,
    )


def test_init(dumb_obs):
    std_obs_types = dict(
        G=('C1C', 'L1C', 'D1C', 'S1C', 'C2S', 'L2S',
           'D2S', 'S2S', 'C2W', 'L2W', 'D2W', 'S2W',
           'C5Q', 'L5Q', 'D5Q', 'S5Q'),
        R=('C1C', 'L1C', 'D1C', 'S1C', 'C2P', 'L2P', 'D2P', 'S2P', 'C2C', 'L2C',
           'D2C', 'S2C'),
        E=('C1C', 'L1C', 'D1C', 'S1C', 'C5Q', 'L5Q', 'D5Q', 'S5Q', 'C7Q',
           'L7Q', 'D7Q', 'S7Q', 'C8Q', 'L8Q', 'D8Q', 'S8Q'),
        J=('C1C', 'L1C', 'D1C', 'S1C', 'C2S', 'L2S', 'D2S', 'S2S', 'C5Q', 'L5Q',
           'D5Q', 'S5Q'),
        S=('C1C', 'L1C', 'D1C', 'S1C'),
        C=('C2I', 'L2I', 'D2I', 'S2I', 'C7I', 'L7I', 'D7I', 'S7I'),
    )

    assert dumb_obs.obs_types == std_obs_types
    assert dumb_obs.time_system == 'GPS'


def test_obs_slice_indices(dumb_obs):
    std_slices = (
        [3, 19], [19, 35], [35, 51], [51, 67], [67, 83], [83, 99], [99, 115],
        [115, 131], [131, 147], [147, 163],
        [163, 179], [179, 195], [195, 211], [211, 227], [227, 243], [243, 259]
    )
    test_slices = dumb_obs._obs_slice_indices()
    assert std_slices == test_slices


def test_indices_according_priority(dumb_obs):
    sat_system = 'J'

    indices = namedtuple('observation_indices', ['phase', 'pseudo_range'])

    std_indices = indices(
        {1: 1, 2: 5},
        {1: 0, 2: 4},
    )
    test_indices = dumb_obs.indices_according_priority(sat_system)

    assert std_indices == test_indices


def test_parse_epoch_record(dumb_obs):
    epoch_record = '> 2015 12 19 00 00  0.0000000  0 28'
    std_epoch_values = (datetime(2015, 12, 19), 0, 28, timedelta(0))
    test_epoch_values = dumb_obs._parse_epoch_record(epoch_record)
    assert std_epoch_values == test_epoch_values

    epoch_record = '>                              4  1'
    std_epoch_values = (None, 4, 1, timedelta(0))
    test_epoch_values = dumb_obs._parse_epoch_record(epoch_record)
    assert std_epoch_values == test_epoch_values


def test_parse_obs_record(dumb_obs):
    """Codes
       G   16 C1C L1C D1C S1C C2S L2S D2S S2S C2W L2W D2W S2W C5Q L5Q D5Q S5Q
    """
    row = 'G05  22730608.640   119450143.06408      3001.057          48.850' \
          '    22730607.500    93078040.86407' \
          '      2338.485          44.050    22730606.840    93078053.86507' \
          '      2338.485          42.350'

    observation_records = namedtuple('observation_records',
                                     ['satellite', 'records'])
    std_obs = observation_records(
        satellite='G05',
        records=(
            ('C1C', 22730608.640, 0, 0),
            ('L1C', 119450143.064, 0, 8),
            ('D1C', 3001.057, 0, 0),
            ('S1C', 48.850, 0, 0),
            ('C2S', 22730607.500, 0, 0),
            ('L2S', 93078040.864, 0, 7),
            ('D2S', 2338.485, 0, 0),
            ('S2S', 44.050, 0, 0),
            ('C2W', 22730606.840, 0, 0),
            ('L2W', 93078053.865, 0, 7),
            ('D2W', 2338.485, 0, 0),
            ('S2W', 42.350, 0, 0),
            ('C5Q', 0, 0, 0),
            ('L5Q', 0, 0, 0),
            ('D5Q', 0, 0, 0),
            ('S5Q', 0, 0, 0),
        )
    )

    test_obs = dumb_obs._parse_obs_record(row)
    assert test_obs == std_obs


def test_next_tec(obs):
    for tec in obs:
        break

    assert tec.satellite == 'G06'
    assert tec.timestamp == datetime(2017, 6, 26, 0)
    assert tec.phase_tec == 33.756676401749395
    assert tec.p_range_tec == -40.183956990827824


def test_attr(attr_obs):
    sat_sys = 'G'
    test_indeces = ({1: 9, 2: 11}, {1: 0, 2: 3})
    indices = attr_obs.indices_according_priority(sat_sys)

    assert test_indeces == indices
