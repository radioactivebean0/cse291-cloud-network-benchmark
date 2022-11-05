
def calculate_retransmission(json_content: dict):
    streams = json_content["intervals"]
    # Calculate retransmission per socket
    retransmissions = [stream["streams"][0]["retransmits"] / stream["streams"][0]["socket"] for stream in streams]
    return retransmissions


def calculate_latency(json_content: dict):
    streams = json_content["intervals"]
    # Calculate latency in miliseconds per socket
    latencies = [stream["streams"][0]["seconds"] / stream["streams"][0]["socket"] * 1000 for stream in streams]
    return latencies


def calculate_jitter(json_content: dict):
    streams = json_content["intervals"]
    # Calculate latency in miliseconds per socket
    latencies = [stream["streams"][0]["seconds"] / stream["streams"][0]["socket"] * 1000 for stream in streams]
    jitters = []
    for latency1, latency2 in zip(latencies[1:], latencies[:-1]):
        jitters.append(abs(latency1 - latency2))
    return jitters
