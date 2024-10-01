from typing import Optional



def check_axon_exists(
    metagraph: "bittensor.metagraph",
    hotkey: str,
    ip_address: Optional[str] = None,
    coldkey: Optional[str] = None,
) -> bool:
    # Iterate through all axons in the metagraph
    for axon in metagraph.axons:
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
        return True

    # If no matching axon was found, return False
    return False
