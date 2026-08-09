Apigee acts as the secure facade between the Agent MCP server and backend enterprise inventory/ERP/customer endpoints.

1. Apigee Proxy Policy: OAuth2 Token Validation & SpikeArrest (apigee-mcp-inventory-facade.xml)
```
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<APIProxy revision="1" name="xyzmart-inventory-v1">
    <ConfigurationVersion majorVersion="4" minorVersion="0"/>
    <Profiles>
        <Profile name="SecurityProfile">
            <!-- 1. Enforce Traffic Spike Protection -->
            <Policy name="SpikeArrest-Limits"/>
            <!-- 2. Validate Agent OAuth2 Bearer Token -->
            <Policy name="OAuthV2-VerifyAccessToken"/>
        </Profile>
    </Profiles>
    <PreFlow name="PreFlow">
        <Request>
            <Step>
                <Name>SpikeArrest-Limits</Name>
            </Step>
            <Step>
                <Name>OAuthV2-VerifyAccessToken</Name>
            </Step>
        </Request>
        <Response/>
    </PreFlow>
</APIProxy>
```

2. Apigee Policy Definitions
SpikeArrest Policy (policies/SpikeArrest-Limits.xml):
```
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<SpikeArrest async="false" continueOnError="false" enabled="true" name="SpikeArrest-Limits">
    <DisplayName>SpikeArrest Limits</DisplayName>
    <Properties/>
    <Identifier ref="request.header.X-Forwarded-For"/>
    <MessageWeight ref="request.header.weight"/>
    <Rate>30pm</Rate>
</SpikeArrest>
```


OAuth2 Verification Policy (policies/OAuthV2-VerifyAccessToken.xml):
```
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<OAuthV2 async="false" continueOnError="false" enabled="true" name="OAuthV2-VerifyAccessToken">
    <DisplayName>Verify Access Token</DisplayName>
    <Operation>VerifyAccessToken</Operation>
    <AccessToken ref="request.header.Authorization"/>
    <Scopes>
        <Scope>customer:read</Scope>
        <Scope>inventory:read</Scope>
        <Scope>backorder:write</Scope>
    </Scopes>
</OAuthV2>
```