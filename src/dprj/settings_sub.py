# -*- coding: utf-8 -*-
import settings_sub_props
from enviroment_type import EnvironmentType
import socket

# ホントはローカルIPが欲しいのだが127.0.0.1しか取れなくなるケースがあるので.
SERVER_HOSTNAME = socket.gethostname()

if settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.LOCAL:
    from settings_sub_local import *
elif settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.DEVELOP:
    from settings_sub_dev import *
elif settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.STAGING:
    from settings_sub_stg import *
elif settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.RELEASE:
    from settings_sub_rel import *
elif settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.MANAGER:
    from settings_sub_mgr import *
elif settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.DEVELOP_TAKI:
    from settings_sub_taki import *
elif settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.DEVELOP_PC:
    from settings_sub_devpc import *
elif settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.DEVELOP_PC_SHINSEI:
    from settings_sub_shinseipc import *
elif settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.RELEASE_PC:
    from settings_sub_relpc import *
