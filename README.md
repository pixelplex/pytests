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

### Note:
Before running the tests, you can specify a environment variables *BASE_URL*, *NATHAN*, *ECHO_POOL*. 
For this you need, example:
* Linux OS: export BASE_URL=_[needed_url]()_
* Windows OS: set BASE_URL=_[needed_url]()_

After that you can use following commands:
    
Filter                       | lcc commands
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

_note:_ can combine run options, for example - `$ lcc run --failed --from-report reports/report-2`

## To Do Lists

### Apis:

#### [Login API](https://echo-dev.io/developers/apis/login-api/#login-api)

- [x] [login](https://echo-dev.io/developers/apis/login-api/#loginstring-user-string-password)

#### [Asset API](https://echo-dev.io/developers/apis/asset-api/#asset-api)

- [x] [get_asset_holders](https://echo-dev.io/developers/apis/asset-api/#get_asset_holdersstring-asset_id-int-start-int-limit)
- [x] [get_asset_holders_count](https://echo-dev.io/developers/apis/asset-api/#get_asset_holders_countstring-asset_id)
- [x] [get_all_asset_holders](https://echo-dev.io/developers/apis/asset-api/#get_all_asset_holders)

#### [Database API](https://echo-dev.io/developers/apis/database-api/#database-api)

- [x] [get_global_properties](https://echo-dev.io/developers/apis/database-api/#get_global_properties)
- [x] [get_required_fees](https://echo-dev.io/developers/apis/database-api/#get_required_feesops-id)
- [ ] [get_objects](https://echo-dev.io/developers/apis/database-api/#get_objectsarray-ids)  
- [x] [set_subscribe_callback](https://echo-dev.io/developers/apis/database-api/#set_subscribe_callbackcallback-notify_remove_create)
- [ ] [set_pending_transaction_callback](https://echo-dev.io/developers/apis/database-api/#set_pending_transaction_callbackcallback)
- [x] [set_block_applied_callback ](https://echo-dev.io/developers/apis/database-api/#set_block_applied_callbackcallback)
- [ ] [cancel_all_subscriptions](https://echo-dev.io/developers/apis/database-api/#cancel_all_subscriptions)
- [x] [get_block_header](https://echo-dev.io/developers/apis/database-api/#get_block_headerblock_num)
- [x] [get_block](https://echo-dev.io/developers/apis/database-api/#get_blockblock_num)
- [ ] [get_transaction](https://echo-dev.io/developers/apis/database-api/#get_transactionblock_num-trx_in_block)
- [ ] [get_recent_transaction_by_id](https://echo-dev.io/developers/apis/database-api/#get_recent_transaction_by_idid)
- [x] [get_chain_properties](https://echo-dev.io/developers/apis/database-api/#get_chain_properties)
- [x] [get_config](https://echo-dev.io/developers/apis/database-api/#get_config)
- [x] [get_chain_id](https://echo-dev.io/developers/apis/database-api/#get_chain_id)
- [x] [get_dynamic_global_properties](https://echo-dev.io/developers/apis/database-api/#get_dynamic_global_properties)
- [ ] [get_key_references](https://echo-dev.io/developers/apis/database-api/#get_key_referenceskeys)
- [x] [get_accounts](https://echo-dev.io/developers/apis/database-api/#get_accountsaccount_ids)
- [ ] [get_full_accounts](https://echo-dev.io/developers/apis/database-api/#get_full_accountsnames_or_ids-subscribe)
- [x] [get_account_by_name](https://echo-dev.io/developers/apis/database-api/#get_account_by_namename)
- [ ] [get_account_references](https://echo-dev.io/developers/apis/database-api/#get_account_referencesaccount_id)
- [ ] [lookup_account_names](https://echo-dev.io/developers/apis/database-api/#lookup_account_namesaccount_names)
- [ ] [lookup_accounts](https://echo-dev.io/developers/apis/database-api/#lookup_accountslower_bound_name-limit)
- [x] [get_account_count](https://echo-dev.io/developers/apis/database-api/#get_account_count)
- [ ] [get_account_balances](https://echo-dev.io/developers/apis/database-api/#get_account_balancesid-assets)
- [ ] [get_named_account_balances](https://echo-dev.io/developers/apis/database-api/#get_named_account_balancesname-assets)
- [ ] [get_balance_objects](https://echo-dev.io/developers/apis/database-api/#get_balance_objectsaddrs)
- [ ] [get_vested_balances](https://echo-dev.io/developers/apis/database-api/#parameters_16)
- [ ] [get_vesting_balances](https://echo-dev.io/developers/apis/database-api/#get_vesting_balancesaccount_id)
- [ ] [get_assets](https://echo-dev.io/developers/apis/database-api/#get_assetsasset_ids)
- [ ] [list_assets](https://echo-dev.io/developers/apis/database-api/#list_assetslower_bound_symbol-limit)
- [ ] [lookup_asset_symbols](https://echo-dev.io/developers/apis/database-api/#lookup_asset_symbolssymbols_or_ids)
- [ ] [get_limit_orders](https://echo-dev.io/developers/apis/database-api/#get_limit_ordersa-b-limit)
- [ ] [get_committee_members](https://echo-dev.io/developers/apis/database-api/#get_committee_memberscommittee_member_ids)
- [ ] [get_committee_member_by_account](https://echo-dev.io/developers/apis/database-api/#get_committee_member_by_accountaccount)
- [ ] [lookup_committee_member_accounts](https://echo-dev.io/developers/apis/database-api/#lookup_committee_member_accountslower_bound_name-limit)
- [ ] [lookup_vote_ids](https://echo-dev.io/developers/apis/database-api/#lookup_vote_idsvotes)
- [ ] [get_transaction_hex](https://echo-dev.io/developers/apis/database-api/#get_transaction_hextrx)
- [ ] [get_required_signatures](https://echo-dev.io/developers/apis/database-api/#get_required_signaturestrx-available_keys)
- [ ] [get_potential_signatures](https://echo-dev.io/developers/apis/database-api/#get_potential_signaturestrx)
- [ ] [verify_authority](https://echo-dev.io/developers/apis/database-api/#verify_authoritytrx)
- [ ] [verify_account_authority](https://echo-dev.io/developers/apis/database-api/#verify_account_authorityname_or_id-signers)
- [ ] [validate_transaction](https://echo-dev.io/developers/apis/database-api/#validate_transactiontrx)
- [ ] [get_proposed_transactions](https://echo-dev.io/developers/apis/database-api/#get_proposed_transactionsid)
- [ ] [get_contract_logs](https://echo-dev.io/developers/apis/database-api/#get_contract_logscontract_id-from-to)
- [ ] [subscribe_contract_logs](https://echo-dev.io/developers/apis/database-api/#subscribe_contract_logscallback-contract_id-from-to)
- [ ] [get_contract_result](https://echo-dev.io/developers/apis/database-api/#get_contract_resultresult_contract_id)
- [ ] [get_contract](https://echo-dev.io/developers/apis/database-api/#get_contractcontract_id)
- [ ] [call_contract_no_changing_state](https://echo-dev.io/developers/apis/database-api/#call_contract_no_changing_statecontract_id-registrar_account-asset_type-code)
- [x] [get_contracts](https://echo-dev.io/developers/apis/database-api/#get_contractscontract_ids)
- [ ] [get_contract_balances](https://echo-dev.io/developers/apis/database-api/#get_contract_balances-contract_id)

#### [History API](https://echo-dev.io/developers/apis/history-api/#history-api)

- [x] [get_account_history](https://echo-dev.io/developers/apis/history-api/#get_account_historyaccount-stop-limit-100-start)
- [x] [get_relative_account_history](https://echo-dev.io/developers/apis/history-api/#get_relative_account_historyaccount-stop-0-limit-100-start-0)
- [x] [get_account_history_operations](https://echo-dev.io/developers/apis/history-api/#get_account_history_operations-account-operation_id-start-stop-limit-100)
- [x] [get_contract_history](https://echo-dev.io/developers/apis/history-api/#get_contract_history-account-stop-limit-start)

#### [Network broadcast API](https://echo-dev.io/developers/apis/network-broadcast-api/#network-broadcast-api)

- [ ] [broadcast_transaction](https://echo-dev.io/developers/apis/network-broadcast-api/#broadcast_transactionsigned_transaction)
- [ ] [broadcast_block](https://echo-dev.io/developers/apis/network-broadcast-api/#broadcast_blocksigned_block)
- [ ] [broadcast_transaction_with_callback](https://echo-dev.io/developers/apis/network-broadcast-api/#broadcast_transaction_with_callbackcallback-trx)
- [ ] [broadcast_transaction_synchronous ](https://echo-dev.io/developers/apis/network-broadcast-api/#broadcast_transaction_synchronous-trx)

#### [Registration API](https://echo-dev.io/developers/apis/registration-api/#registration-api)

- [x] [register_account](https://echo-dev.io/developers/apis/registration-api/#register_accountname-owner_key-active_key-memo_key-echorand_key)

### Operations:

#### [List of Account Management Operations](https://echo-dev.io/developers/operations/#account-management)

- [ ] [account_create_operation](https://echo-dev.io/developers/operations/account_management/_account_create_operation/)
- [ ] [account_update_operation](https://echo-dev.io/developers/operations/account_management/_account_update_operation/)
- [ ] [account_whitelist_operation](https://echo-dev.io/developers/operations/account_management/_account_whitelist_operation/)
- [ ] [account_upgrade_operation](https://echo-dev.io/developers/operations/account_management/_account_upgrade_operation/)
- [ ] [account_transfer_operation](https://echo-dev.io/developers/operations/account_management/_account_transfer_operation/)
    
#### [List of Assert Conditions Operations](https://echo-dev.io/developers/operations/#assert-conditions)

- [ ] [assert_operation](https://echo-dev.io/developers/operations/assert_conditions/_assert_operation/)
    
#### [List of Asset Management Operations](https://echo-dev.io/developers/operations/#asset-management)

- [ ] [asset_create_operation](https://echo-dev.io/developers/operations/asset_management/_asset_create_operation/)
- [ ] [asset_global_settle_operation](https://echo-dev.io/developers/operations/asset_management/_asset_global_settle_operation/)
- [ ] [asset_settle_operation](https://echo-dev.io/developers/operations/asset_management/_asset_settle_operation/)
- [ ] [asset_settle_cancel_operation [VIRTUAL]](https://echo-dev.io/developers/operations/asset_management/_asset_settle_cancel_operation/)
- [ ] [asset_fund_fee_pool_operation](https://echo-dev.io/developers/operations/asset_management/_asset_fund_fee_pool_operation/)
- [ ] [asset_update_operation](https://echo-dev.io/developers/operations/asset_management/_asset_update_operation/)
- [ ] [asset_update_bitasset_operation](https://echo-dev.io/developers/operations/asset_management/_asset_update_bitasset_operation/)
- [ ] [asset_update_feed_producers_operation](https://echo-dev.io/developers/operations/asset_management/_asset_update_feed_producers_operation/)
- [ ] [asset_publish_feed_operation](https://echo-dev.io/developers/operations/asset_management/_asset_publish_feed_operation/)
- [ ] [asset_issue_operation](https://echo-dev.io/developers/operations/asset_management/_asset_issue_operation/)
- [ ] [asset_reserve_operation](https://echo-dev.io/developers/operations/asset_management/_asset_reserve_operation/)
- [ ] [asset_claim_fees_operation](https://echo-dev.io/developers/operations/asset_management/_asset_claim_fees_operation/)
    
#### [List of Balance Object Operations](https://echo-dev.io/developers/operations/#balance-object)

- [ ] [balance_claim_operation](https://echo-dev.io/developers/operations/balance_object/_balance_claim_operation/)

#### [List of For Committee Members Operations](https://echo-dev.io/developers/operations/#for-committee-members)

- [ ] [committee_member_create_operation](https://echo-dev.io/developers/operations/committee_member/_committee_member_create_operation/)
- [ ] [committee_member_update_operation](https://echo-dev.io/developers/operations/committee_member/_committee_member_update_operation/)
- [ ] [committee_member_update_global_parameters_operation](https://echo-dev.io/developers/operations/committee_member/_committee_member_update_global_parameters_operation/)
    
#### [List of Contract Operations](https://echo-dev.io/developers/operations/#contract-operations)

- [ ] [create_contract_operation](https://echo-dev.io/developers/operations/contracts/_create_contract_operation/)
- [ ] [call_contract_operation](https://echo-dev.io/developers/operations/contracts/_call_contract_operation/)
- [ ] [contract_transfer_operation [VIRTUAL]](https://echo-dev.io/developers/operations/contracts/_contract_transfer_operation/)
    
#### [List of Custom Extension Operations](https://echo-dev.io/developers/operations/#custom-extension)

- [ ] [custom_operation](https://echo-dev.io/developers/operations/custom/_custom_operation/)

#### [List of Assets Market Operations](https://echo-dev.io/developers/operations/#assets-market)

- [ ] [limit_order_create_operation](https://echo-dev.io/developers/operations/asset_market/_limit_order_create_operation/)
- [ ] [limit_order_cancel_operation](https://echo-dev.io/developers/operations/asset_market/_limit_order_cancel_operation/)
- [ ] [call_order_update_operation](https://echo-dev.io/developers/operations/asset_market/_call_order_update_operation/)
- [ ] [fill_order_operation [VIRTUAL]](https://echo-dev.io/developers/operations/asset_market/_fill_order_operation/)
- [ ] [bid_collateral_operation](https://echo-dev.io/developers/operations/asset_market/_bid_collateral_operation/)
- [ ] [execute_bid_operation [VIRTUAL]](https://echo-dev.io/developers/operations/asset_market/_execute_bid_operation/)

#### [List of Proposal Operations](https://echo-dev.io/developers/operations/#proposal-operations)

- [ ] [proposal_create_operation](https://echo-dev.io/developers/operations/proposals/_proposal_create_operation/)
- [ ] [proposal_update_operation](https://echo-dev.io/developers/operations/proposals/_proposal_update_operation/)
- [ ] [proposal_delete_operation](https://echo-dev.io/developers/operations/proposals/_proposal_delete_operation/)

#### [List of Asset Transfer Operations](https://echo-dev.io/developers/operations/#asset-transfer)

- [ ] [transfer_operation](https://echo-dev.io/developers/operations/asset_transfer/_transfer_operation/)
- [ ] [override_transfer_operation](https://echo-dev.io/developers/operations/asset_transfer/_override_transfer_operation/)
    
#### [List of Vesting Balances Operations](https://echo-dev.io/developers/operations/#vesting-balances)

- [ ] [vesting_balance_create_operation](https://echo-dev.io/developers/operations/vesting_balances/_vesting_balance_create_operation/)
- [ ] [vesting_balance_withdraw_operation](https://echo-dev.io/developers/operations/vesting_balances/_vesting_balance_withdraw_operation/)
    
#### [List of Withdrawal Permissions Operations](https://echo-dev.io/developers/operations/#withdrawal-permissions)

- [ ] [withdraw_permission_create_operation](https://echo-dev.io/developers/operations/withdraw_permission/_withdraw_permission_create_operation/)
- [ ] [withdraw_permission_update_operation](https://echo-dev.io/developers/operations/withdraw_permission/_withdraw_permission_update_operation/)
- [ ] [withdraw_permission_claim_operation](https://echo-dev.io/developers/operations/withdraw_permission/_withdraw_permission_claim_operation/)
- [ ] [withdraw_permission_delete_operation](https://echo-dev.io/developers/operations/withdraw_permission/_withdraw_permission_delete_operation/)
