from typing import Optional, Any, Dict, List


def get_axon_data(
    metagraph: "bittensor.metagraph",
    hotkey: str,
    ip_address: Optional[str] = None,
    coldkey: Optional[str] = None,
) -> dict:
    # Iterate through all axons in the metagraph
    for i, axon in enumerate(metagraph.axons):
        # If an ip_address is provided, check it
        if axon.hotkey != hotkey:
            continue

        # Check if the hotkey matches
        if ip_address is not None and axon.ip != ip_address:
            continue  # Skip this axon if the IP doesn't match

        # If a cold_key is provided, check it
        if coldkey is not None and axon.coldkey != coldkey:
            continue  # Skip this axon if the coldkey doesn't match

        # If all checks pass, return True
        return dict(exists=True, stake=float(metagraph.stake[i]))

    # If no matching axon was found, return False
    return dict(exists=False)


def get_hotkey_to_uid(metagraph: "bittensor.metagraph") -> List[Dict[str, Any]]:
    return [dict(uid=i, hotkey=a.hotkey) for i, a in enumerate(metagraph.axons)]
