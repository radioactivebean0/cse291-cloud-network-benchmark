

def calculate_retransmission(json_content: dict):
    protocol = json_content["start"]["test_start"]["protocol"]
    if protocol == "TCP":
        streams = json_content["intervals"]
        retransmissions = [stream["streams"][0]["retransmits"] for stream in streams]
        return sum(retransmissions) / len(retransmissions)
    else:
        # protocol == "UDP"
        raise ValueError("UDP protocol does not support retransmission")


def calculate_latency(json_content: dict):
    streams = json_content["intervals"]
    latencies = [stream["streams"][0]["seconds"] * 1000 for stream in streams]
    return sum(latencies) / len(latencies)


def calculate_jitter(json_content: dict):
    protocol = json_content["start"]["test_start"]["protocol"]
    if protocol == "TCP":
        streams = json_content["intervals"]
        latencies = [stream["streams"][0]["seconds"] * 1000 for stream in streams]
        jitters = []
        for latency1, latency2 in zip(latencies[1:], latencies[:-1]):
            jitters.append(abs(latency1 - latency2))
        return sum(jitters) / len(jitters)
    else:
        return json_content["end"]["streams"][0]["udp"]["jitter_ms"]
