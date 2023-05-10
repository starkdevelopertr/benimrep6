import logging
import time
import forta_agent
from web3 import Web3
from forta_agent import get_json_rpc_url, Finding
from concurrent.futures import ThreadPoolExecutor

from src.main import run_all
from src.constants import attacker_bots, ATTACKER_CONFIDENCE, N_WORKERS, MAX_FINDINGS

logging.basicConfig(filename=f"logs.log", level=logging.INFO, 
                    format='%(levelname)s:%(asctime)s:%(name)s:%(lineno)d:%(message)s')
logger = logging.getLogger(__name__)

web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))


def run_all_extended(central_node, alert_event):
    try:
        attackers_df, graph_statistics = run_all(central_node)
    except Exception as e:
        logger.error(f"{central_node}:\tError running run_all in a thread: {e}")
        return []
    # Now we put things into a list of findings
    all_findings_list = []
    finding_dict = {
            'name': 'scammer-label-propagation',
            'description': 'Address marked as scammer by label propagation',
            'alert_id': 'SCAMMER-LABEL-PROPAGATION-1',
            'severity': forta_agent.FindingSeverity.High,
            'type': forta_agent.FindingType.Scam
        }
    if attackers_df.shape[0] > MAX_FINDINGS:
        logger.error(f"{central_node}:\tToo many attackers found: {attackers_df.shape[0]}. Labels may be compromised")
    else:
        for row_idx in range(attackers_df.shape[0]):
            attacker_info = attackers_df.iloc[row_idx]
            logger.info(f'{central_node}:\tNew attacker info: {attacker_info}')
            label_dict = {
                'entity': attacker_info.name,
                'label': 'scammer-eoa',
                'confidence': attacker_info['n_predicted_attacker']/10 * attacker_info['mean_probs_attacker'],
                'entity_type': forta_agent.EntityType.Address,
                'metadata': {
                    'central_node': central_node,
                    'central_node_alert_id': alert_event.alert.alert_id,
                    'central_node_alert_name': alert_event.alert.name,
                    'central_node_alert_hash': alert_event.alert.hash,
                    'graph_statistics': graph_statistics,
                }
            }
            finding_dict['labels'] = [forta_agent.Label(label_dict)]
            all_findings_list.append(Finding(finding_dict))
    return all_findings_list
        
        
def initialize():
    global executor
    executor = ThreadPoolExecutor(max_workers=N_WORKERS)
    global addresses_analyzed
    addresses_analyzed = []
    global global_futures
    global_futures = {}
    global global_alerts
    global_alerts = []

    subscription_json = []
    chain_id = web3.eth.chain_id
    for bot in attacker_bots:
        subscription_json.append({"botId": bot, "chainId": chain_id})
    alert_config = {"alertConfig": {"subscriptions": subscription_json}}
    logger.info(f"Initializing scammer label propagation bot. Subscribed to bots successfully: {alert_config}")
    return alert_config


def provide_handle_alert(w3):
    logger.debug("provide_handle_alert called")
    

    def handle_alert(alert_event: forta_agent.alert_event.AlertEvent) -> list:
        logger.debug("handle_alert inner called")
        logger.debug(f"AlertId:{alert_event.alert_id};\tName:{alert_event.name};\tAlertHash:{alert_event.hash};\tBotId{alert_event.bot_id}")
        t = time.time()
        global executor
        global addresses_analyzed
        global global_futures

        list_of_addresses = []
        if alert_event.alert.alert_id == 'SCAM-DETECTOR-ADDRESS-POISONING':
            logger.info(f"Address poisoning. Addresses: {';'.join([label.entity for label in alert_event.alert.labels])}")
            return []
        for label in alert_event.alert.labels:
            if label.confidence >= ATTACKER_CONFIDENCE and label.entity_type == forta_agent.EntityType.Address:
                list_of_addresses.append(label.entity)
        list_of_addresses = list(set(list_of_addresses))
        for address in list_of_addresses:
            if address not in addresses_analyzed:
                logger.debug(f"Adding address {address} to the pool")
                global_futures[address] = executor.submit(run_all_extended, address, alert_event)
                addresses_analyzed.append(address)
        logger.info(f"Alert {alert_event.alert.alert_id}:\t{time.time() - t:.10f} s. {len(list_of_addresses)} addresses: {';'.join(list_of_addresses)}")
        return []

    return handle_alert


real_handle_alert = provide_handle_alert(web3)


def handle_alert(alert_event: forta_agent.alert_event.AlertEvent) -> list:
    logger.debug("handle_alert called")
    return real_handle_alert(alert_event)


def provide_handle_block(w3):
    logger.debug("provide_handle_block called")

    def handle_block(block_event) -> list:
        logger.debug("handle_block inner called")
        t = time.time()
        global global_futures
        global global_alerts

        completed_futures = []
        running_futures = 0
        pending_futures = 0
        for address, future in global_futures.items():
            if future.running():
                running_futures += 1
            elif future.done():
                try:
                    global_alerts += future.result()
                    completed_futures.append(address)
                except Exception as e:
                    logger.error(f"Exception {e} occurred while collecting results from address {address}")
            else:
                pending_futures += 1
        for address in completed_futures:
            global_futures.pop(address)
        # We return the first MAX_FINDINGS findings, and remove them from the list. Otherwise
        # we cache them in global alerts and will return them in the next block
        alerts = global_alerts[:MAX_FINDINGS]
        global_alerts = global_alerts[MAX_FINDINGS:]
        logger.info(f"Block {block_event.block_number}:\tRF:{running_futures};PF:{pending_futures};\t {time.time() - t:.10f} s;\t{len(alerts)} findings")
        return alerts

    return handle_block


real_handle_block = provide_handle_block(web3)

def handle_block(block_event) -> list:
    logger.debug("handle_block called")
    return real_handle_block(block_event)