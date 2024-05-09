# BitAds - Decentralized Advertising on Bittensor

**Revolutionizing Online Advertising with Decentralization. Discover how BitAds leverages the Bittensor Network to offer cost-effective, high-quality advertising through a unique incentive mechanism for miners and validators.**
![alt text](docs/bitads.png)


:no_entry_sign:**The Problem:**

The current advertising landscape, particularly as shaped by the web2 paradigm, presents significant challenges not only for the users who are subjected to ads but also for the companies that invest heavily in advertising. At the heart of these challenges are the highly centralized tech organizations that dominate and control the industry, such as Google AdSense, Facebook Audience Network, and Apple Advertising. This centralized control results in a significant power imbalance, lack of transparency, and high costs. 

:bulb:**The Solution:**

The BitAds network emerges as a revolutionary solution, harnessing the power of blockchain technology to foster a decentralized and incentivised advertising environment. By reimagining the foundational principles of advertising transactions, BitAds seeks to rectify the issues of transparency, fraud, inefficiency, and the high costs associated with conventional advertising methods.

:link:**Usefull Links:** <br>

Subnet Video Presentation: https://www.youtube.com/watch?v=5vJjnIrzMLk <br>
Whitepaper: https://bitads.ai/whitepaper <br>
Roadmap: https://bitads.ai/roadmap <br>
API Docs: https://bitads.ai/api <br>
GitHub: https://github.com/eseckft/BitAds.ai

# The BitAds.ai Ecosystem

**1. Validators, Miners, and BitAds Core:**

Validators create and manage advertising campaigns using the BitAds Core platform, which provides tools for creating landing pages and tracking campaign performance. <br><br>
Miners generate unique links for campaigns to promote across the internet. They are rewarded with TAO tokens for driving organic traffic to these links. BitAds Core acts as the central platform for campaign management, traffic analysis, and miner validation.

**2. Incentive Mechanism:**
Miners are incentivized with TAO tokens, not based on the client's payment offer, but on the organic traffic they attract. This system ensures cost-effective advertising for clients while rewarding miners substantially for their efforts.
<br>
![alt text](docs/bitads_diagram.png)

# Integration with Bittensor

BitAds leverages Bittensor’s decentralized network to distribute advertising tasks among miners. <br><br>
Initially, BitAds will focus on promoting the Bittensor project itself, demonstrating the network's marketing capabilities and incentivizing participation. <br><br>
Taking into consideration the potential emission of the subnet, this will potentially serve as the most powerful marketing engine for the Bittensor project. <br><br>
By harnessing the collaborative efforts of the network's participants, BitAds aims to significantly enhance the visibility and adoption of Bittensor, establishing a robust foundation for the future growth of both BitAds and Bittensor.

# The First Incentivized Campaign
![alt text](docs/bittensor_campaign.png)<br>
The first campaign ["Join the Bittensor Revolution where AI meets the Decentralization"](https://x.bitads.ai/lty9sdtvcg55s/) on the BitAds Network will be BittensorWiki, a platform where you can find everything you need to know about the Bittensor Network. <br>
In fact, this campaign will serve as a powerful marketing tool for the Bittensor Network, as miners will be incentivized to generate organic traffic for the BittensorWiki campaign. <br>
https://bittensorwiki.com

# FirstAds.ai - The First Web App
<p align="center">
  <img src="docs/firstads.png" alt="Description of Image" width="50%" />
</p>

The first application developed on the BitAds subnet is FirstAds. This platform enables users to create and promote their campaigns, incentivizing BitAds miners to generate organic traffic for these campaigns at a minimal cost. <br>
https://firstads.ai

# Advantages of BitAds.ai

:globe_with_meridians:**Decentralization** <br>
BitAds emphasizes optimal decentralization by ensuring a broad distribution of miners and validators.

:moneybag:**Cost-Effectiveness** <br>
By operating on low-cost systems requirements and incentivizing miners with TAO tokens, BitAds offers a highly economical advertising solution for both parties, clients and promoters.

:gem:**Quality Traffic** <br>
The incentive mechanism encourages miners to drive high-quality organic traffic to their links.

:star:**Miners Competition** <br>
Miners are motivated to outperform each other in attracting the best traffic to clients' websites, in order to generate more rewards. This competition enhances the effectiveness of advertising campaigns, ensuring that clients will receive optimal visibility and engagement.

# Income Sources for Validators
:white_check_mark:**Validators can monetize their participation in BitAds.ai Subnet through various avenues, including:** <br>
- promoting their own products <br>
- engaging in affiliate marketing (for example - Amazon Affiliate Program, ClickBank) <br>
- developing applications using the BitAds.ai API <br>
- offering paid API access to others

# Scoring Mechanism

The scoring formula for BitAds miners incorporates a thoughtful approach to quantifying the effectiveness and impact of miners based on multiple key performance indicators: 

**1. Unique visits (UV)** <br>
This measures the total number of distinct visitors directed to the campaign via the miner's unique link. It's a direct indicator of the reach and traffic generated by the miner.

**2. Total visits (TV)** <br>
Total number of visits directed to the campaign via the miner's unique link.

**3. Click through rate (CTR)** <br>
Expressed as a decimal, this metric captures the efficiency of the campaign in engaging visitors. Specifically, it measures the proportion of visitors who click the "call to action" button and resolve the captha if prompted. A CTR of 5% is represented as 0.05, for example.

**4. Maximum expected values (UVmax and CTRmax)** <br>
These thresholds are set to normalize the unique visits and CTR, ensuring they're scaled to a value between 0 and 1. This normalization facilitates a fair comparison between miners, accounting for varying scales of performance. Let's say UVmax is set to 1000, and CTRmax is 0.15.  

**Normalization is performed as follows:** <br>
```bash
Unorm = UV / UVmax
CTRnorm = CTR / CTRmax
```
**5. Weight of parameters (Wuv and Wctr)** <br>
These weights reflect the relative importance of Unique visits and CTR in calculating the miner's score. By adjusting these weights, you can balance the importance on traffic generation versus engagement. 

In our model, both parameters are equally valued:
```bash
Wuv = 0.5
Wctr = 0.5
```
**6. Artificial traffic indicator (ATI)** <br>
This parameter will calculate the level of artificial traffic, which will be based on two different metrics (OTS and UVPS), representing organic traffic score and unique visits percentage score.
```bash
ATI = (Wots * OTS) + (Wuvps * UVPS)
```
**7. "Wots" and "Wuvps"** <br> 
Represents the weights of OTS and UVPS parameters. By adjusting these values we can decide on the importance of each parameter relative to the other when calculating the ATI.
```bash
Wots (weights organic traffic score) = 0.5 
Wuvps (weights unique visits percentage score) = 0.5
```
**8. Organic traffic score (OTS)** <br>
This parameter will calculate the percentage of organic traffic, by excluding the artificial traffic from the unique visits.
```bash
OTS = 1 - (AT / UV)
```
**9. Artificial traffic (AT)** <br>
This parameter will count all the artificial traffic, based on multiple metrics that takes into account the user's behavior. 

**10. Unique visits percentage score (UVPS)** <br>
This parameter will calculate the percentage of unique visits.
```bash
UVPS = UV / TV
```

**All the values needed for Score Calculation:** <br>

```bash
UV - the number of Unique visitors
CTR - the click-through rate (as a decimal)
Unorm = U / Umax
CTRnorm = CTR / CTRmax
Wuv - Weight for Unique Visitors = 0.5
Wctr - Weight for CTR = 0.5
ATI - Artificial traffic indicator = ATI = (Wots * OTS) + (Wuvps * UVPS)
AT - Artifical traffic
OTS - Organic traffic score = (1- (AT / V))
UVPS - Unique visits percentage = (UV / TV)
Wots - Weight for organic traffic score = 0.5
Wuvps - Weight for unique visits percentage = 0.5

FINAL MINER SCORE = (( Wuv * Unorm ) + ( Wctr * CTRnorm )) * ATI, where ATI = (Wots * OTS) + (Wuvps * UVPS)
FINAL MINER SCORE = (( Wuv * Unorm ) + ( Wctr * CTRnorm )) * ((Wots * OTS) + (Wuvps * UVPS))
```
Example:
```bash
UVmax = 1000
CTRmax = 0.15
Weights: Wu = 0.5 ; Wc = 0.5
Weights: Wots = 0.5 ; Wuvps = 0.5
```
Miner scenario:
```bash
- TV = 10000
- UV = 1000
- CTR = 0.05
- UA = 100
- DPDV = 200
- VWI = 300
```
The score will be calculated:
```bash
Unorm = 1000/1000 = 1
CTRnorm = 0.05/0.15 = 0.33
AT = 600
OTS = (1 - (600/1000) = 1 - 0.6 = 0.4
UVPS = 1000 / 10000 = 0.1

FINAL MINER SCORE = (( Wu * Unorm ) + ( Wc * CTRnorm )) * ((Wots * OTS) + (Wuvps * UVPS))
                  = ((0.5 * 1) + (0.5 * 0.33)) * ((0.5 * 0.4) + (0.5 * 0.10))
                  = (0.5 + 0.165) * (0.2 + 0.05)
                  = 0.665 * 0.205
                  = 0.13632
```
Conditions:
```bash
- if MINER SCORE > 1, MINER SCORE = 1. 
- miner Score will have maximum 5 decimals.
```

# Subnet Security 

**BitAds campaigns have multiple levels of protection against fraudulent activity such as bot or script-driven fake activity. In particular, verification for human authenticity occurs through:**
- AWS WAF [(Well-Architected Framework) ](https://aws.amazon.com/waf/)
- CAPTCHA

All incoming requests are forwarded to AWS WAF for inspection by the web ACL. <br>

AWS WAF is a web security service that helps protect web applications from common web threats such as SQL injections, cross-site scripting (XSS), and cross-site request forgery (CSRF). <br>

Human Verification Check is an additional layer of protection in AWS WAF, designed to help distinguish humans from bots. It is useful for preventing automated attacks such as DDoS attacks and spam. 
In BitAds.ai architecture it is one of the levels of protection against traffic manipulation. <br>

Each time the BidAds.ai API is accessed, validators' and miners' scripts transmit their Bittensor wallet keys for verification of their presence in the registered users' database. BidAds also checks the status of each user (whether they are active or blocked), as well as the compatibility of validators' and miners' script code versions with the current version provided by BitAds.ai developers. This, on the one hand, requires users to constantly update their scripts and prevents unauthorized interference with them. <br>

Additionally, every 30 minutes, there is an update of the lists of allowed participants in the process. Miners receive a list of validators, and validators receive a list of miners with whom they can communicate. This way, the system is protected from external intrusion.

# Roadmap

1. **Decentralized Data and Campaign Management** <br>
- Miners and validators will now collect data separately. Only data that matches across all participants will be used to ensure accuracy.
- All data on visits will be stored locally on each participant's server, improving security and access speed.
- Active campaigns will run without interruption, even if the BitAds API is down. While new campaigns cannot be initiated until the API is restored, all other subnetwork operations will continue to function seamlessly.

2. **Conversion Tracking** <br>
- Begin by integrating conversion tracking functionality within BitAds to accurately measure conversion rates on client websites. This will provide valuable insights into the effectiveness of advertisements and user interactions.
- Integrate BitAds plugins with Shopify and WooCommerce to seamlessly track conversions from advertising campaigns. This enables more accurate data collection and improves marketing optimizations directly within the e-commerce platforms.
- Redirect 90% of the incentive towards conversions (sales), while allocating the remaining 10% for visits and clicks.

3. **Template and Design Expansion** <br>
Add more templates, colors, and layouts to BitAds landing pages.

4. **Device Targeting** <br>
Implement device targeting feature to specify desired traffic source.

5. **Performance Analytics** <br>
Implement daily performance analytics for validators to enhance campaign monitoring.

6. **Geo-Location** <br>
Implement geo-location filtering to enable validators and clients to specify desired traffic origins in BitAds.

7. **Campaign Information Bot** <br>
Launch an interactive discord/telegram bot to provide miners with immediate access to campaign information and notifications.

8. **Traffic Source Analysis** <br>
Implement traffic source analysis to precisely track visitor origins.

9. **Domain Selection Expansion** <br>
Expand landing page domains to enable validators and clients to select from a wider range of options.



# Creating a Wallet

Before proceeding, you'll need to create a wallet. A wallet is required for managing your digital assets and interacting with the functionalities provided by this repository.

Detailed instructions on how to create a wallet can be found in the official documentation [here](https://docs.bittensor.com/getting-started/wallets).

Please ensure that you follow the steps outlined in the documentation carefully to set up your wallet correctly.

# Registration in Subnetwork

To fully utilize the functionalities provided by this repository, it is necessary to register within the BitAds.ai Subnetwork (UID 16). 
```bash
btcli subnet register --netuid 16 --wallet.name <name> --wallet.hotkey <name>
```

# Usage of Scripts

Please note that the usage of scripts within this repository is restricted to registered users of [BitAds.ai](https://BitAds.ai)

To utilize any scripts provided here, you must first sign up and authenticate yourself on the [BitAds.ai](https://BitAds.ai) platform. Once registered, you will be granted access to the necessary resources and functionalities. 

**The validators will be manually approved after we receive written confirmation on Discord about their registration.**

For any inquiries regarding script usage or registration, please refer to the official documentation on [BitAds.ai](https://BitAds.ai) or contact our support team.

# Installation Guide

To begin using this repository, the first step is to install Bittensor. Bittensor is a prerequisite for running the scripts and tools provided here. 

You can find detailed installation instructions for Bittensor in the official documentation [here](https://docs.bittensor.com/getting-started/installation).

Please make sure to follow the installation steps carefully to ensure that Bittensor is properly set up on your system before proceeding with any other operations.

If you encounter any issues during the installation process, refer to the troubleshooting section in the Bittensor documentation or reach out to our support team for assistance.

**Prerequisites:**
- Ensure that you have Python 3.12 or a later version installed on your system.
- Run your local Subtensor, instructions on how to install Subtensor locally can be found here: [Subtensor Installation Guide](https://github.com/opentensor/subtensor/blob/main/docs/running-subtensor-locally.md)

```basg 
git clone https://github.com/eseckft/BitAds.ai.git
cd BitAds.ai
python3 -m pip install -e .
python3 setup.py install_lib
python3 setup.py build
```

**After registration, you can start the miner script using the following command:**

# With autoupdates

```bash
pm2 start run_miner_auto_update.py --interpreter python3 -- --netuid 16 --subtensor.network local --wallet.name <name> --wallet.hotkey <name> --logging.debug
```

**And for running the validator script, use:**

```bash
pm2 start run_validator_auto_update.py --interpreter python3 -- --netuid 16 --subtensor.network local --wallet.name <name> --wallet.hotkey <name> --logging.debug
```

# Without auto updates

```bash
python neurons/miner.py --netuid 16 --subtensor.network local --wallet.name <name> --wallet.hotkey <name> --logging.debug
```

**And for running the validator script, use:**

```bash
python neurons/validator.py --netuid 16 --subtensor.network local --wallet.name <name> --wallet.hotkey <name> --logging.debug
```
