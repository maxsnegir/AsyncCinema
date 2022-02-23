from jaeger_client import Config

_config = {
    "sampler": {
        "type": "const",
        "param": 1,
    },
    "local_agent": {
        "reporting_host": "jaeger",
        "reporting_port": 6831,
    },
    "logging": True,
}


def _setup_jaeger():
    config = Config(
        config=_config,
        service_name='auth-service',
        validate=True,
    )
    return config.initialize_tracer()
