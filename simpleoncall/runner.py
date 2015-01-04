from logan.runner import run_app


def generate_settings():
    return "from simpleoncall.settings import *"


def main():
    run_app(
        project='simpleoncall',
        default_config_path='~/.simpleoncall/simpleoncall.py',
        default_settings='simpleoncall.settings',
        settings_initializer=generate_settings,
        settings_envvar='SIMPLEONCALL_CONF',
    )

if __name__ == '__main__':
    main()
