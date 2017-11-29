# -*- coding: utf-8 -*-

developer_ip = [
#    '211.9.52.232',        # プラチナエッグ（211.9.52.232/29）.
#    '211.9.52.233',
#    '211.9.52.234',
#    '211.9.52.235',
#    '211.9.52.236',
#    
#    '211.9.52.237',        # 串.
#    '211.9.52.238',
#    '211.9.52.239',
#    
#    '202.94.133.44',        # NinjaEgg(札幌).
#    '61.45.192.115',        # NinjaEgg(大阪).
#    '219.118.180.66',       # NinjaEgg(アキバ).
#    '182.171.230.100',      # プラチナエッグ本郷.
#    '61.117.209.10',        # 引き継ぎ先
#    '202.140.221.28',       # 引き継ぎ先
    '118.238.253.172',      # 引き続き先
#    '139.196.173.86',       # 引き続き先
    '123.56.64.124',        # 引き続き先
#    '39.110.207.20',        # 
#    '116.80.254.141',       #
#    '220.152.109.134',      #
#    '182.171.253.143',      #
#    '116.58.190.97',        #
#    '175.179.109.26',       #
#    '175.179.114.111',      #
#    '175.179.111.160',      #
#    '115.177.179.166',      #
#    
#
    '10.116.41.20',       # 管理ツール.
    '10.116.41.11',       # 管理ノード.
]

# DMM スマホ版のコンフィグ.
applications = {
    '127799' : {        # 開発環境.
       'consumer_key' : '0dyl7xmDuwmvRrsl',
       'consumer_secret' : 'VNGb63LaqAYaZLZPPi2NJ[b6xplcJGpm',
       'developer_ip' : developer_ip,
       'developer_id' : [
            '261905',
            '7276430',
            '4629670',
        ],
        'sandbox' : True,
    },
    '607183' : {        # 開発環境.
       'consumer_key' : 'xAFaxdI5Ir2CCkyJ',
       'consumer_secret' : 'uAK#tHaCRHs7zRe0dO1ESvzmPrTcDcRY',
       'developer_ip' : developer_ip,
       'developer_id' : [
            '261905',
            '7276430',
            '4629670',
        ],
        'sandbox' : True,
    },
    '297627' : {        # ステージング.
       'consumer_key' : 'nHFE2hTAuBoBrKEf',
       'consumer_secret' : 'YDjJwJa3j7LldkgsWR2OZI_e?pJo5]vK',
       'developer_ip' : developer_ip,
       'developer_id' : [
            '261905',
            '7276430',
            '4629670',
            '2588824',
        ],
        'sandbox' : True,
    },
    '340004' : {                # 本番環境.
       'consumer_key' : 'U7fd2bDhOou5VeN6',
       'consumer_secret' : 'zifjiExm]?8MgEm7Bs-ttBC?S08B4Jxl',
       'developer_ip' : developer_ip,
       'developer_id' : [
            '11060984',
            '13434336',
            '1412759',
            '11830507',
            '15471365',
            '23427632',
            '28774432',
            '11739356',
            '2588824',
            '28978730'
            '20174324',
        ],
        'sandbox' : False,
    },
    '402286' : {                # 開発環境devpc.
       'consumer_key' : 'MGwHCtaFizURRus2',
       'consumer_secret' : '1#Q$sgB#d-QVBRa_jAMQXMg6[8LVn6N?',
       'developer_ip' : developer_ip,
       'developer_id' : [
            '261905',
            '7276430',
            '4629670',
        ],
        'sandbox' : True,
    },
    '635899' : {
       'consumer_key' : 'Uq563akoti3zaA0I',
       'consumer_secret' : 'RXRgAHFS7OxDLWCu@xq7xCeTL[dLB$ga',
       'developer_ip' : [],
       'developer_id' : [
            '261905',
            '7276430',
            '4629670',
        ],
        'sandbox' : True,
    },
    '119733' : {        # 開発環境(旧).
       'consumer_key' : 'YYKZxNv108fNMK7k',
       'consumer_secret' : 'WF3tYzK3gzA[$CtZo9NPJ$Gz8M]Hi?U5',
       'developer_ip' : developer_ip,
       'developer_id' : [
            '261905',
            '7276430',
            '4629670',
        ],
        'sandbox' : True,
    },
    '24663' : {        # CSC開発環境.
       'consumer_key' : 'lk3wdGZTVH7hEZx4',
       'consumer_secret' : 'ksd8ru5s2MIKq3zD@s3a3RZNkXWTLeMW',
       'developer_ip' : developer_ip,
       'developer_id' : [
            '6355001',
            '668294',
        ],
        'sandbox' : True,
    },
    '107669' : {        # CSCステージング環境.
       'consumer_key' : '6HkgoYqhzlLVaR4Y',
       'consumer_secret' : '4]#dR$Ed1SGEBRkxlwFBjXJM$hw-5qZR',
       'developer_ip' : developer_ip,
       'developer_id' : [
            '668294',
        ],
        'sandbox' : True,
    },
}
