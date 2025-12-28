FOL Vocabulary & Predicate Schema

## Constants / Terms by Category

### actors

- `google`
- `user`
- `users`
- `you`

### contexts

- `account`
- `app`
- `apps`
- `browser`
- `browsers`
- `controls`
- `device`
- `devices`
- `services`
- `settings`
- `google account`
- `privacy controls`

### data_types

- `content`
- `data`
- `identifiers`
- `information`
- `ip address`
- `personal information`
- `unique identifier`
- `unique identifiers`

### technologies

- `cookies`
- `logs`
- `server logs`

### purposes

- `abuse`
- `communicate`
- `deliver`
- `fraud`
- `improve`
- `keep`
- `maintain`
- `personalize`
- `preferences`
- `protect`
- `provide`
- `security`

### retention

- `auto-delete`
- `delete`

### reasons

- `business`
- `legal`
- `legal needs`

### other

- `about`
- `accessible`
- `across`
- `add`
- `address`
- `ads`
- `against`
- `allow`
- `also`
- `and`
- `are`
- `associated`
- `auto`
- `based`
- `become`
- `can`
- `choose`
- `collected`
- `collects`
- `comments`
- `create`
- `date`
- `depending`
- `details`
- `develop`
- `different`
- `documents`
- `emails`
- `engines`
- `explains`
- `features`
- `for`
- `have`
- `how`
- `including`
- `intended`
- `interaction`
- `its`
- `kept`
- `kinds`
- `like`
- `longer`
- `manage`
- `many`
- `may`
- `name`
- `needs`
- `not`
- `number`
- `options`
- `order`
- `other`
- `password`
- `payment`
- `periods`
- `personal`
- `phone`
- `photos`
- `policy`
- `privacy`
- `privately`
- `publicly`
- `receive`
- `referrer`
- `retains`
- `risks`
- `search`
- `server`
- `sessions`
- `share`
- `shared`
- `signed`
- `some`
- `specific`
- `store`
- `such`
- `technical`
- `technologies`
- `that`
- `the`
- `them`
- `this`
- `through`
- `time`
- `under`
- `unique`
- `upload`
- `url`
- `use`
- `used`
- `uses`
- `using`
- `vary`
- `way`
- `what`
- `when`
- `which`
- `while`
- `why`
- `with`
- `working`
- `your`
- `privacy policy`


## Predicate Signatures

- `collects/2`: collects(Actor, DataType)
- `collects_content/2`: collects_content(Actor, ContentType)
- `collects_tech_data/2`: collects_tech_data(Actor, TechDataType)
- `uses_technology/2`: uses_technology(Actor, Technology)
- `uses_for/2`: uses_for(Actor, Purpose)
- `purpose/3`: purpose(Actor, DataType, Purpose)
- `varies_by/2`: varies_by(Process, Factor)  % e.g., varies_by(data_collection, privacy_controls)
- `stores_under_identifier/4`: stores_under_identifier(Actor, IdentifierType, Context, Purpose)
- `retains/3`: retains(Actor, DataType, RetentionPolicy)
- `allows_setting/2`: allows_setting(Actor, SettingAction)  % e.g., delete/auto_delete
- `may_keep_longer_for/3`: may_keep_longer_for(Actor, DataType, Reason)
