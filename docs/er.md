# ER Diagram

```plantuml
@startuml
' hide the spot
' hide circle

' avoid problems with angled crows feet
skinparam linetype ortho

entity "ChargePoint" as chargepoint {
    * **chargepoint_id**: CharField[255]
    * chargepoint_model: CharField[20] {optional}
    * chargepoint_vendor: CharField[20] {optional}
    * chargebox_serial_number: CharField[20] {optional}
    * chargepoint_serial_number: CharField[25] {optional}
    * firmware_version: CharField[50] {optional}
    * ip_address: CharField[15]
    * websocket_port: IntegerField
    * connected: BooleanField
    * chargepoint_status: CharField[11]
    * ocpp_version: CharField[9]
    * last_heartbeat: DateTimeField
    * <u>location</u>: Location
}

entity "ChargingProfile" as chargingprofile {
    * **chargingprofile_id**: IntegerField
    * <u>transaction_id</u>: Transaction {optional}
    * stack_level: IntegerField
    * chargingprofile_purpose: CharField[21]
    * recurrency_kind: CharField[10] {optional}
    * valid_from: DateTimeField {optional}
    * valid_to: DateTimeField {optional}
    * duration: IntegerField {optional}
    * start_schedule: DateTimeField {optional}
    * charging_rate_unit: CharField[1]
    * chargingschedule_period: ArrayField[JSONField{}]
    * min_charging_rate: DecimalField {optional}
}

entity "Connector" as connector {
    * **uuid**: UUIDField
    * connectorid: IntegerField
    * availability_status: CharField[11]
    * connector_status: CharField[13]
    * <u>chargepoint</u>: Chargepoint
}

entity "Heartbeat" as heartbeat {
    * timestamp: DateTimeField
    * <u>chargepoint</u>: Chargepoint
}

entity "IdTag" as idtag {
    * **idToken**: CharField[255]
    * expiry_date: DateTimeField[] {optional}
    * revoked: BooleanField
    * <u>user</u>: User {optional}
}

entity "Reservation" as reservation {
    * **uuid**: UUIDField
    * <u>connector</u>: Connector
    * reservation_id: IntegerField
    * expiry_date: DateTimeField
}

entity "StatusNotification" as statusnotification {
    * <u>connector</u>: Connector
    * error_code: CharField[50]
    * info: CharField[50] {optional}
    * status: CharField[50]
    * timestamp: DateTimeField {optional}
    * vendor_id: CharField[255] {optional}
    * vendor_error_code: CharField[50] {optional}
}

entity "Transaction" as transaction {
    * **transaction_id**: AutoField
    * start_transaction_timestamp: DateTimeField
    * stop_transaction_timestamp: DateTimeField {optional}
    * wh_meter_start: IntegerField
    * wh_meter_stop: IntegerField {optional}
    * wh_meter_last: IntegerField
    * <u>id_tag</u>: IdTag
    * reason_stopped: CharField[50] {optional}
    * status: CharField[15]
}

entity "User" as user {

}

entity "Profile" as profile {
    * <u>user</u>: User
    * image: ImageField
    * timezone: TimezoneField
}

entity "Location" as location {
    * **uuid**: UUIDField
    * country: CharField[20]
    * postal_code: CharField[20]
    * street_address: CharField[255]
    * city: CharField[20]
    * type: ???
    * name: CharField
}

chargepoint }|--|| location
connector }|-- chargepoint

user ||--o{ idtag
user ||--|| profile

transaction }o--|| idtag

heartbeat }o--|| chargepoint

reservation }o--|| connector

transaction }o--o| chargingprofile

statusnotification }|--|| connector

@enduml
```
