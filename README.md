# BitAds - Decentralized Advertising on the Bittensor Network

The Problem:

The current advertising landscape, particularly as shaped by the web2 paradigm, presents significant challenges not only for the users who are subjected to ads but also for the companies that invest heavily in advertising. At the heart of these challenges are the highly centralized tech organizations that dominate and control the industry, such as Google AdSense, Facebook Audience Network, and Apple Advertising. This centralized control results in a significant power imbalance, lack of transparency, and high costs. 

The Solution:

The BitAds network emerges as a revolutionary solution, harnessing the power of blockchain technology to foster a decentralized and incentivised advertising environment. By reimagining the foundational principles of advertising transactions, BitAds seeks to rectify the issues of transparency, fraud, inefficiency, and the high costs associated with conventional advertising methods.

1st Campaign:

The first campaign on the BitAds Network will be BittensorWiki, a platform where you can find everything you need to know about the Bittensor Network. In fact, this campaign will serve as a powerful marketing tool for the Bittensor Network, as miners will be incentivized to generate organic traffic for the BittensorWiki campaign.
https://bittensorwiki.com

1st Web App:

The first application developed on the BitAds subnet is FirstAds. This platform enables users to create and promote their campaigns, incentivizing BitAds miners to generate organic traffic for these campaigns at a minimal cost. 
https://firstads.ai

# Usage of Scripts

Please note that the usage of scripts within this repository is restricted to registered users of bitads.ai. 

To utilize any scripts provided here, you must first sign up and authenticate yourself on the bitads.ai platform. Once registered, you will be granted access to the necessary resources and functionalities.

For any inquiries regarding script usage or registration, please refer to the official documentation on bitads.ai or contact our support team.

# Installation Guide

To begin using this repository, the first step is to install Bittensor. Bittensor is a prerequisite for running the scripts and tools provided here. 

You can find detailed installation instructions for Bittensor in the official documentation [here](https://docs.bittensor.com/getting-started/installation).

Please make sure to follow the installation steps carefully to ensure that Bittensor is properly set up on your system before proceeding with any other operations.

If you encounter any issues during the installation process, refer to the troubleshooting section in the Bittensor documentation or reach out to our support team for assistance.

# Creating a Wallet

Before proceeding, you'll need to create a wallet. A wallet is required for managing your digital assets and interacting with the functionalities provided by this repository.

Detailed instructions on how to create a wallet can be found in the official documentation [here](https://docs.bittensor.com/getting-started/wallets).

Please ensure that you follow the steps outlined in the documentation carefully to set up your wallet correctly.

# Registration in Subnetwork \<ID\>

To fully utilize the functionalities provided by this repository, it is necessary to register within Subnetwork 5. 

Registration in Subnetwork \<ID\> allows you to access specific features and resources tailored to your needs.

```bash
btcli subnet register --netuid <id> --wallet.name <name> --wallet.hotkey <name>
```

# Running Scripts

To execute the commands at the root of the project, you can follow these steps:

- Install the project in editable mode using pip:
```basg 
python3 -m pip install -e .
```
- Install the project's library:
```basg 
python3 setup.py install_lib
```
- Build the project:
```basg 
python3 setup.py build
```

After registration, you can start the miner script using the following command:

```bash
python neurons/miner.py --netuid <id> --wallet.name <name> --wallet.hotkey <name> --logging.debug --logging.trace
```

And for running the validator script, use:

```bash
python neurons/validator.py --netuid <id> --wallet.name <name> --wallet.hotkey <name> --logging.debug --logging.trace
```
