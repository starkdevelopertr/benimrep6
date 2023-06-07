# Scam Detector Bot Release Notes

## v0.2.2 (June 6th 2023 - beta)
- refactor of label to avoid deduping. Prior to version 0.2.2 a label was either scammer-eoa or scammer-contract with alertId in the metadata giving additional context. Now, the label itself with have this context in the form of 'scammer-eoa/threat_category', e.g. 'scammer-eoa/ice-phishing'. A subscriber can still query all scammer labels using a wildcard query, e.g. scammer* or scammer-eoa*
- enhance handleFP function to remove specific labels as well as remove labels comprehensively

## v0.2.1 (June 2nd 2023 - beta)
- add handler type into alert description

## v0.2.0 (June 1st 2023 - beta)
- introduction of additional handler that assesses alerts for a given EOA utililizing a supervised machine learning model for combination alerts. For version 0.2.0, if either the traditional combination heuristic or the ML model raise an alert, both alerts will be raised. A flag 'handler_type' in the metadata will allow to differentiate what algorithm was used. 


## v0.1.33 (May 30th 2023 - beta)
- better handling of contracts that base bots alerted on. the associated scammer-contract labels will be decorated with the appropriate alert_id whereas other contracts deployed by the same scammer will receive an generic "SCAM-DETECTOR-SCAMMER-DEPLOYED-CONTRACT" alert_id.
- enhanced the handleTx contract creation to also add pool contract creations (e.g. uniswap pools)
- add original alert hashes in metadata of emitted label; unified meta data fields for different types of labels for consistency
- incorporate [token impersonation bot](https://explorer.forta.network/bot/0x6aa2012744a3eb210fc4e4b794d9df59684d36d502fd9efe509a867d0efa5127) as a passthrough alert: SCAM-DETECTOR-IMPERSONATING-TOKEN
- integrated new alerts from the [ice phishing bot](https://explorer.forta.network/bot/0x8badbf2ad65abc3df5b1d9cc388e419d9255ef999fb69aac6bf395646cf01c14): ICE-PHISHING-PULL-SWEEPTOKEN and ICE-PHISHING-OPENSEA-PROXY-UPGRADE. The former allows an scammer to create a transfer transaction using a multicall with pull and sweepToken function; the latter, the scammer can trick a user to upgrading the implementation of a user's opensea proxy contract to the attacker's implementation, which gives the attacker control over user's assets. 
- integrated new alert from the [label propagation bot](https://explorer.forta.network/bot/0xcd9988f3d5c993592b61048628c28a7424235794ada5dc80d55eeb70ec513848): SCAMMER-LABEL-PROPAGATION-2 which operates on a global as opposed to local label propagation graph model.

## v0.1.32 (May 18th 2023 - beta)
- upgrade to latest SDK (1.1.16/ 0.1.32)
- add SCAM-DETECTOR-SCAMMER-ASSOCIATION alert for when account is associated with a scammer account as per the [label propagation bot](https://explorer.forta.network/bot/0xcd9988f3d5c993592b61048628c28a7424235794ada5dc80d55eeb70ec513848)
- change alert caching to be per threat category, such that an alert/label gets emitted per threat category observed as opposed to only reporting the first threat category observed

## v0.1.26 (May 16th 2023 - beta)
- add SCAM-DETECTOR-SCAMMER-DEPLOYED-CONTRACT alert for when a known scammer deploys a contract

## v0.1.25 (May 16th 2023 - beta)
- add manual alerting capability; these alerts will be flagged with alert id: SCAM-DETECTOR-MANUAL- [ THREAT-CATEGORY ], e.g. SCAM-DETECTOR-MANUAL-ICE-PHISHING
- restricted the contract similarity bot to only operate on scams where a contract is essential:
    - SCAM-DETECTOR-SOCIAL-ENG-NATIVE-ICE-PHISHING
    - SCAM-DETECTOR-ADDRESS-POISONER

## v0.1.21 (May 10 2023 - beta)
- tune confidence based on April precision numbers
- switched from fraudulent seaport order to the [scammer nft trader bot](https://explorer.forta.network/bot/0x513ea736ece122e1859c1c5a895fb767a8a932b757441eff0cadefa6b8d180ac), which covers additional on-chain market places (blur, looksrare and seaport). Renamed alertId SCAM-DETECTOR-FRAUDULENT-SEAPORT-ORDER to SCAM-DETECTOR-FRAUDULENT-NFT-ORDER as a result.

## v0.1.20 (May 4th 2023 - beta)
- incorporated [hard rug pull](https://explorer.forta.network/bot/0xc608f1aff80657091ad14d974ea37607f6e7513fdb8afaa148b3bff5ba305c15
), [soft rug pull](https://explorer.forta.network/bot/0x1a6da262bff20404ce35e8d4f63622dd9fbe852e5def4dc45820649428da9ea1
) and [rake token bot](https://explorer.forta.network/bot/0x36be2983e82680996e6ccc2ab39a506444ab7074677e973136fa8d914fc5dd11). New corresonding alerts are emitted: SCAM-DETECTOR-HARD-RUG-PULL, SCAM-DETECTOR-SOFT-RUG-PULL, and SCAM-DETECTOR-RAKE-TOKEN
- expanded coverage for native ice phishing to include NIP-5/ NIP-6 of the [native ice phishing bot](https://explorer.forta.network/bot/0x1a69f5ec8ef436e4093f9ec4ce1a55252b7a9a2d2c386e3f950b79d164bc99e0). NIP-5/ NIP-6 are flagging native ice phishing where a contract is involved using static and dynamic detection approaches.
- incorporated [contract similarity bot](https://explorer.forta.network/bot/0x3acf759d5e180c05ecabac2dbd11b79a1f07e746121fc3c86910aaace8910560
); this bot will expand on previously raised alerts utilizing contract code similarity. A new alert is emitted: SCAM-DETECTOR-SIMILAR-CONTRACT

## v0.1.19 (May 9th 2023 - prod; May 1st 2023 - beta)
- refactored bot from utilizing graphQL library to handleAlert. This speeds up alerts.
- added sharding support to ensure no alerts are being dropped due to processing time of the alerts
- added persistence of findings/alerts cache, so no findings/alerts are lost upon a reassignment or restart
- fixes various parsing issues of base bot alerts
