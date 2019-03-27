# Automated Tests for Echo 
The project is intended for testing Echo. Includes testing:
* [Api](https://echo-dev.io/developers/apis/)
* [Operations](https://echo-dev.io/developers/operations/)
* Testing according to specified scenarios

## Installation

### Manual installation:

    $ git clone https://gitlab.pixelplex.by/631_echo/pytests.git
    $ cd pytests
    $ virtualenv venv
    $ .\venv\Scripts\activate
    $ pip install -r requirements.txt

## Usage

    
**Filter**                       | **lcc commands**
---------------------------------|----------------------
Run all tests                    | `$ lcc run`
Run tests with special tag       | `$ lcc run -a tag_name`
Run tests with special property  | `$ lcc run -m property_kind:property_name`
Run tests with special link      | `$ lcc run -l link_name`
Run only passed tests            | `$ lcc run --passed`
Run only failed tests            | `$ lcc run --failed`
Run only skipped tests           | `$ lcc run --skipped`
Run only non-passed tests        | `$ lcc run --non-passed`
Run only disabled tests          | `$ lcc run --disabled`
Run only enabled tests           | `$ lcc run --enabled`
Run tests from special report    | `$ lcc run --from-report path_to_report`

**_note:_** can combine run options, for example - `$ lcc run --failed --from-report reports/report-2`

## To Do Lists

### Apis:

#### [Login API](https://echo-dev.io/developers/apis/login-api/#login-api)

![](https://img.shields.io/badge/coverage-all_methods-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Methods:
1) **[login](https://echo-dev.io/developers/apis/login-api/#loginstring-user-string-password)**  
![](https://img.shields.io/badge/2_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [x] login with empty credential
    - [x] login with valid credential
    ###### Negative:
    - [ ] login with no valid credential

#### [Asset API](https://echo-dev.io/developers/apis/asset-api/#asset-api)

![](https://img.shields.io/badge/coverage-all_methods-green.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Methods: 

1) **[get_asset_holders](https://echo-dev.io/developers/apis/asset-api/#get_asset_holdersstring-asset_id-int-start-int-limit)**  
![](https://img.shields.io/badge/2_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/5_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive: 
    - [x] method main check
    - [x] get info about the new asset holders
    ###### Negative:
    - [x] use in method call nonexistent asset_id
    - [x] call method without params
    - [x] call method with wrong params of all types
    - [x] call method with nonstandard params
    - [x] call method with more then limit params
    
2) **[get_asset_holders_count](https://echo-dev.io/developers/apis/asset-api/#get_asset_holders_countstring-asset_id)**  
![](https://img.shields.io/badge/2_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/3_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive: 
    - [x] method main check
    - [x] add holders to new asset
    - [x] work of start and limit params
    ###### Negative:
    - [x] use in method call nonexistent asset_id
    - [x] call method without params
    - [x] call method with wrong params of all types
    
3) **[get_all_asset_holders](https://echo-dev.io/developers/apis/asset-api/#get_all_asset_holders)**  
![](https://img.shields.io/badge/3_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/1_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [x] method main check
    - [x] new asset without holders
    - [x] new asset with holders
    ###### Negative:
    - [x] call method with params of all types

#### [Database API](https://echo-dev.io/developers/apis/database-api/#database-api)

![](https://img.shields.io/badge/coverage-2_method(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Methods:
1) **[get_objects](https://echo-dev.io/developers/apis/database-api/#get_objectsarray-ids)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
2) **[set_subscribe_callback](https://echo-dev.io/developers/apis/database-api/#set_subscribe_callbackcallback-notify_remove_create)**   
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)**
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
3) **[set_pending_transaction_callback](https://echo-dev.io/developers/apis/database-api/#set_pending_transaction_callbackcallback)**   
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
4) **[set_block_applied_callback ](https://echo-dev.io/developers/apis/database-api/#set_block_applied_callbackcallback)**   
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
5) **[cancel_all_subscriptions](https://echo-dev.io/developers/apis/database-api/#cancel_all_subscriptions)**   
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
6) **[get_block_header](https://echo-dev.io/developers/apis/database-api/#get_block_headerblock_num)**   
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
7) **[get_block](https://echo-dev.io/developers/apis/database-api/#get_blockblock_num)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
8) **[get_transaction](https://echo-dev.io/developers/apis/database-api/#get_transactionblock_num-trx_in_block)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
9) **[get_recent_transaction_by_id](https://echo-dev.io/developers/apis/database-api/#get_recent_transaction_by_idid)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_  

10) **[get_chain_properties](https://echo-dev.io/developers/apis/database-api/#get_chain_properties)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
11) **[get_global_properties](https://echo-dev.io/developers/apis/database-api/#get_global_properties)**  
![](https://img.shields.io/badge/1_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/1_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [x] method main check
    ###### Negative:
    - [x] call method with params of all types
    
11) **[get_config](https://echo-dev.io/developers/apis/database-api/#get_config)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
13) **[get_chain_id](https://echo-dev.io/developers/apis/database-api/#get_chain_id)  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)**
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
14) **[get_dynamic_global_properties](https://echo-dev.io/developers/apis/database-api/#get_dynamic_global_properties)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
15) **[get_key_references](https://echo-dev.io/developers/apis/database-api/#get_key_referenceskeys)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
16) **[get_accounts](https://echo-dev.io/developers/apis/database-api/#get_accountsaccount_ids)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
17) **[get_full_accounts](https://echo-dev.io/developers/apis/database-api/#get_full_accountsnames_or_ids-subscribe)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
18) **[get_account_by_name](https://echo-dev.io/developers/apis/database-api/#get_account_by_namename)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
19) **[get_account_references](https://echo-dev.io/developers/apis/database-api/#get_account_referencesaccount_id)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
20) **[lookup_account_names](https://echo-dev.io/developers/apis/database-api/#lookup_account_namesaccount_names)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
21) **[lookup_accounts](https://echo-dev.io/developers/apis/database-api/#lookup_accountslower_bound_name-limit)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
22) **[get_account_count](https://echo-dev.io/developers/apis/database-api/#get_account_count)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
23) **[get_account_balances](https://echo-dev.io/developers/apis/database-api/#get_account_balancesid-assets)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
24) **[get_named_account_balances](https://echo-dev.io/developers/apis/database-api/#get_named_account_balancesname-assets)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
25) **[get_balance_objects](https://echo-dev.io/developers/apis/database-api/#get_balance_objectsaddrs)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
26) **[get_vested_balances](https://echo-dev.io/developers/apis/database-api/#parameters_16)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
27) **[get_vesting_balances](https://echo-dev.io/developers/apis/database-api/#get_vesting_balancesaccount_id)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
28) **[get_assets](https://echo-dev.io/developers/apis/database-api/#get_assetsasset_ids)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
29) **[list_assets](https://echo-dev.io/developers/apis/database-api/#list_assetslower_bound_symbol-limit)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
30) **[lookup_asset_symbols](https://echo-dev.io/developers/apis/database-api/#lookup_asset_symbolssymbols_or_ids)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
31) **[get_order_book](https://echo-dev.io/developers/apis/database-api/#get_order_bookbase-quote-depth-50)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
32) **[get_limit_orders](https://echo-dev.io/developers/apis/database-api/#get_limit_ordersa-b-limit)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
33) **[get_call_orders](https://echo-dev.io/developers/apis/database-api/#get_call_ordersa-limit)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
34) **[get_settle_orders](https://echo-dev.io/developers/apis/database-api/#get_settle_ordersa-limit)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
35) **[get_margin_positions](https://echo-dev.io/developers/apis/database-api/#get_margin_positionsid)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
36) **[subscribe_to_market](https://echo-dev.io/developers/apis/database-api/#subscribe_to_marketcallback-a-b)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
37) **[unsubscribe_from_market](https://echo-dev.io/developers/apis/database-api/#unsubscribe_from_marketa-b)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
38) **[get_ticker](https://echo-dev.io/developers/apis/database-api/#get_tickerbase-quote)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
39) **[get_24_volume](https://echo-dev.io/developers/apis/database-api/#get_24_volumebase-quote)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
40) **[get_trade_history](https://echo-dev.io/developers/apis/database-api/#get_trade_historybase-quote-start-stop-limit-100)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
41) **[get_witnesses](https://echo-dev.io/developers/apis/database-api/#get_witnesseswitness_ids)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
42) **[get_witness_by_account](https://echo-dev.io/developers/apis/database-api/#get_witness_by_accountaccount)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
43) **[lookup_witness_accounts](https://echo-dev.io/developers/apis/database-api/#lookup_witness_accountslower_bound_name-limit)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
44) **[get_witness_count](https://echo-dev.io/developers/apis/database-api/#get_witness_count)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
45) **[get_committee_members](https://echo-dev.io/developers/apis/database-api/#get_committee_memberscommittee_member_ids)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
46) **[get_committee_member_by_account](https://echo-dev.io/developers/apis/database-api/#get_committee_member_by_accountaccount)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
47) **[lookup_committee_member_accounts](https://echo-dev.io/developers/apis/database-api/#lookup_committee_member_accountslower_bound_name-limit)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
48) **[get_workers_by_account](https://echo-dev.io/developers/apis/database-api/#get_workers_by_accountaccount_id)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
49) **[lookup_vote_ids](https://echo-dev.io/developers/apis/database-api/#lookup_vote_idsvotes)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
50) **[get_transaction_hex](https://echo-dev.io/developers/apis/database-api/#get_transaction_hextrx)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
51) **[get_required_signatures](https://echo-dev.io/developers/apis/database-api/#get_required_signaturestrx-available_keys)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
52) **[get_potential_signatures](https://echo-dev.io/developers/apis/database-api/#get_potential_signaturestrx)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
53) **[get_potential_address_signatures](https://echo-dev.io/developers/apis/database-api/#get_potential_address_signaturestrx)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
54) **[verify_authority](https://echo-dev.io/developers/apis/database-api/#verify_authoritytrx)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
55) **[verify_account_authority](https://echo-dev.io/developers/apis/database-api/#verify_account_authorityname_or_id-signers)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
56) **[validate_transaction](https://echo-dev.io/developers/apis/database-api/#validate_transactiontrx)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
57) **[get_required_fees](https://echo-dev.io/developers/apis/database-api/#get_required_feesops-id)**  
![](https://img.shields.io/badge/3_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/9_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [x] method main check
    - [x] fee equal to get_required_fee in transfer operation
    - [x] fee higher than get_required_fee in transfer operation
    ###### Negative:
    - [x] call method without params and with insufficient number of params
    - [x] call method with wrong params
    - [x] use in method call nonexistent asset_id
    - [x] fee lower than get_required_fee in transfer operation
    - [x] sender don't have enough fee
    - [x] try to get fee in EETH
    - [x] nonexistent contract byte code
    - [x] nonexistent asset id
    - [x] nonexistent method byte code
    
58) **[get_proposed_transactions](https://echo-dev.io/developers/apis/database-api/#get_proposed_transactionsid)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
59) **[get_all_contracts](https://echo-dev.io/developers/apis/database-api/#get_all_contracts)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
60) **[get_contract_logs](https://echo-dev.io/developers/apis/database-api/#get_contract_logscontract_id-from-to)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
61) **[subscribe_contract_logs](https://echo-dev.io/developers/apis/database-api/#subscribe_contract_logscallback-contract_id-from-to)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
62) **[get_contract_result](https://echo-dev.io/developers/apis/database-api/#get_contract_resultresult_contract_id)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
63) **[get_contract](https://echo-dev.io/developers/apis/database-api/#get_contractcontract_id)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
64) **[call_contract_no_changing_state](https://echo-dev.io/developers/apis/database-api/#call_contract_no_changing_statecontract_id-registrar_account-asset_type-code)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
65) **[get_contracts](https://echo-dev.io/developers/apis/database-api/#get_contractscontract_ids)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
66) **[get_contract_balances](https://echo-dev.io/developers/apis/database-api/#get_contract_balances-contract_id)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_


#### [History API](https://echo-dev.io/developers/apis/history-api/#history-api)

![](https://img.shields.io/badge/coverage-0_method(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Methods:
1) **[get_account_history](https://echo-dev.io/developers/apis/history-api/#get_account_historyaccount-stop-limit-100-start)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
2) **[get_relative_account_history](https://echo-dev.io/developers/apis/history-api/#get_relative_account_historyaccount-stop-0-limit-100-start-0)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
3) **[get_account_history_operations](https://echo-dev.io/developers/apis/history-api/#get_account_history_operations-account-operation_id-start-stop-limit-100)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_
    
4) **[get_contract_history](https://echo-dev.io/developers/apis/history-api/#get_contract_history-account-stop-limit-start)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] _Work In Progress_
    ###### Negative:
    - [ ] _Work In Progress_

#### [Network broadcast API](https://echo-dev.io/developers/apis/network-broadcast-api/#network-broadcast-api)

![](https://img.shields.io/badge/coverage-0_method(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Methods:
1) **[broadcast_transaction](https://echo-dev.io/developers/apis/network-broadcast-api/#broadcast_transactionsigned_transaction)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
2) **[broadcast_block](https://echo-dev.io/developers/apis/network-broadcast-api/#broadcast_blocksigned_block)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
3) **[broadcast_transaction_with_callback](https://echo-dev.io/developers/apis/network-broadcast-api/#broadcast_transaction_with_callbackcallback-trx)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
4) **[broadcast_transaction_synchronous ](https://echo-dev.io/developers/apis/network-broadcast-api/#broadcast_transaction_synchronous-trx)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...

#### [Registration API](https://echo-dev.io/developers/apis/registration-api/#registration-api)

![](https://img.shields.io/badge/coverage-all_methods-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Methods:
1) **[register_account](https://echo-dev.io/developers/apis/registration-api/#register_accountname-owner_key-active_key-memo_key-echorand_key)**  
![](https://img.shields.io/badge/1_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/7_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [x] registration with valid credential
    ###### Negative:
    - [x] registration with empty account name
    - [x] registration with account name length longer than 63
    - [x] registration with account name start with digit
    - [x] registration with account name is digits
    - [x] registration with account name with a special character, not hyphen
    - [x] registration with account name end with a special character
    - [x] registration with account name is uppercase
    - [ ] registration with not valid: owner ECDSA key, active ECDSA key, memo ECDSA key, ed25519 key for echorand

### Operations:

#### [List of Account Management Operations](https://echo-dev.io/developers/operations/#account-management)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[account_create_operation](https://echo-dev.io/developers/operations/account_management/_account_create_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
2) **[account_update_operation](https://echo-dev.io/developers/operations/account_management/_account_update_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
3) **[account_whitelist_operation](https://echo-dev.io/developers/operations/account_management/_account_whitelist_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
4) **[account_upgrade_operation](https://echo-dev.io/developers/operations/account_management/_account_upgrade_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
5) **[account_transfer_operation](https://echo-dev.io/developers/operations/account_management/_account_transfer_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
#### [List of Assert Conditions Operations](https://echo-dev.io/developers/operations/#assert-conditions)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[assert_operation](https://echo-dev.io/developers/operations/assert_conditions/_assert_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
#### [List of Asset Management Operations](https://echo-dev.io/developers/operations/#asset-management)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[asset_create_operation](https://echo-dev.io/developers/operations/asset_management/_asset_create_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
2) **[asset_global_settle_operation](https://echo-dev.io/developers/operations/asset_management/_asset_global_settle_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
3) **[asset_settle_operation](https://echo-dev.io/developers/operations/asset_management/_asset_settle_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
4) **[asset_settle_cancel_operation [VIRTUAL]](https://echo-dev.io/developers/operations/asset_management/_asset_settle_cancel_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests... 
    
5) **[asset_fund_fee_pool_operation](https://echo-dev.io/developers/operations/asset_management/_asset_fund_fee_pool_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
6) **[asset_update_operation](https://echo-dev.io/developers/operations/asset_management/_asset_update_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests... 
    
7) **[asset_update_bitasset_operation](https://echo-dev.io/developers/operations/asset_management/_asset_update_bitasset_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
8) **[asset_update_feed_producers_operation](https://echo-dev.io/developers/operations/asset_management/_asset_update_feed_producers_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
9) **[asset_publish_feed_operation](https://echo-dev.io/developers/operations/asset_management/_asset_publish_feed_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
10) **[asset_issue_operation](https://echo-dev.io/developers/operations/asset_management/_asset_issue_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests... 
    
11) **[asset_reserve_operation](https://echo-dev.io/developers/operations/asset_management/_asset_reserve_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
12) **[asset_claim_fees_operation](https://echo-dev.io/developers/operations/asset_management/_asset_claim_fees_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests... 
    
#### [List of Balance Object Operations](https://echo-dev.io/developers/operations/#balance-object)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[balance_claim_operation](https://echo-dev.io/developers/operations/balance_object/_balance_claim_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
#### [List of For Committee Members Operations](https://echo-dev.io/developers/operations/#for-committee-members)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[committee_member_create_operation](https://echo-dev.io/developers/operations/committee_member/_committee_member_create_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
2) **[committee_member_update_operation](https://echo-dev.io/developers/operations/committee_member/_committee_member_update_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
3) **[committee_member_update_global_parameters_operation](https://echo-dev.io/developers/operations/committee_member/_committee_member_update_global_parameters_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
### [List of Confidential Operations](https://echo-dev.io/developers/operations/#confidential-operations)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[transfer_to_blind_operation](https://echo-dev.io/developers/operations/stealth_transfer/_transfer_to_blind_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
2) **[transfer_from_blind_operation](https://echo-dev.io/developers/operations/stealth_transfer/_transfer_from_blind_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
3) **[blind_transfer_operation](https://echo-dev.io/developers/operations/stealth_transfer/_blind_transfer_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
#### [List of Contract Operations](https://echo-dev.io/developers/operations/#contract-operations)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[create_contract_operation](https://echo-dev.io/developers/operations/contracts/_create_contract_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
2) **[call_contract_operation](https://echo-dev.io/developers/operations/contracts/_call_contract_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
3) **[contract_transfer_operation [VIRTUAL]](https://echo-dev.io/developers/operations/contracts/_contract_transfer_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
#### [List of Custom Extension Operations](https://echo-dev.io/developers/operations/#custom-extension)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[custom_operation](https://echo-dev.io/developers/operations/custom/_custom_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
#### [List of FBA Operations](https://echo-dev.io/developers/operations/#fba)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[fba_distribute_operation [VIRTUAL]](https://echo-dev.io/developers/operations/fba/_fba_distribute_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
#### [List of Assets Market Operations](https://echo-dev.io/developers/operations/#assets-market)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[limit_order_create_operation](https://echo-dev.io/developers/operations/asset_market/_limit_order_create_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
2) **[limit_order_cancel_operation](https://echo-dev.io/developers/operations/asset_market/_limit_order_cancel_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
3) **[call_order_update_operation](https://echo-dev.io/developers/operations/asset_market/_call_order_update_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
4) **[fill_order_operation [VIRTUAL]](https://echo-dev.io/developers/operations/asset_market/_fill_order_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests... 
    
5) **[bid_collateral_operation](https://echo-dev.io/developers/operations/asset_market/_bid_collateral_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
6) **[execute_bid_operation [VIRTUAL]](https://echo-dev.io/developers/operations/asset_market/_execute_bid_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests... 
    
#### [List of Proposal Operations](https://echo-dev.io/developers/operations/#proposal-operations)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[proposal_create_operation](https://echo-dev.io/developers/operations/proposals/_proposal_create_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
2) **[proposal_update_operation](https://echo-dev.io/developers/operations/proposals/_proposal_update_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
3) **[proposal_delete_operation](https://echo-dev.io/developers/operations/proposals/_proposal_delete_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
#### [List of Asset Transfer Operations](https://echo-dev.io/developers/operations/#asset-transfer)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[transfer_operation](https://echo-dev.io/developers/operations/asset_transfer/_transfer_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
2) **[override_transfer_operation](https://echo-dev.io/developers/operations/asset_transfer/_override_transfer_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
#### [List of Vesting Balances Operations](https://echo-dev.io/developers/operations/#vesting-balances)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[vesting_balance_create_operation](https://echo-dev.io/developers/operations/vesting_balances/_vesting_balance_create_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
2) **[vesting_balance_withdraw_operation](https://echo-dev.io/developers/operations/vesting_balances/_vesting_balance_withdraw_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
#### [List of Withdrawal Permissions Operations](https://echo-dev.io/developers/operations/#withdrawal-permissions)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[withdraw_permission_create_operation](https://echo-dev.io/developers/operations/withdraw_permission/_withdraw_permission_create_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
2) **[withdraw_permission_update_operation](https://echo-dev.io/developers/operations/withdraw_permission/_withdraw_permission_update_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
3) **[withdraw_permission_claim_operation](https://echo-dev.io/developers/operations/withdraw_permission/_withdraw_permission_claim_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
4) **[withdraw_permission_delete_operation](https://echo-dev.io/developers/operations/withdraw_permission/_withdraw_permission_delete_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests... 
    
#### [List of Witness Operations](https://echo-dev.io/developers/operations/#witness-operations)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[witness_create_operation](https://echo-dev.io/developers/operations/witnesses/_witness_create_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
2) **[witness_update_operation](https://echo-dev.io/developers/operations/witnesses/_witness_update_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...
    
#### [List of Worker Operations](https://echo-dev.io/developers/operations/#worker-operations)

![](https://img.shields.io/badge/coverage-0_operation(s)-red.svg?style=for-the-badge)
![](https://img.shields.io/badge/WIP-YES-informational.svg?style=for-the-badge)

##### Operations:
1) **[worker_create_operation](https://echo-dev.io/developers/operations/workers/_worker_create_operation/)**  
![](https://img.shields.io/badge/0_positive_test(s)-green.svg?style=plastic?logoColor=violet)
![](https://img.shields.io/badge/0_negative_test(s)-red.svg?style=plastic?logoColor=violet)

    ###### Positive:
    - [ ] a list of tests...
    ###### Negative:
    - [ ] a list of tests...