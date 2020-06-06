# swagger_client.AuthApi

All URIs are relative to *https://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**logout_a_user**](AuthApi.md#logout_a_user) | **POST** /auth/logout | 
[**user_login**](AuthApi.md#user_login) | **POST** /auth/login | 


# **logout_a_user**
> logout_a_user()



### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwtkey
configuration = swagger_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.AuthApi(swagger_client.ApiClient(configuration))

try:
    api_instance.logout_a_user()
except ApiException as e:
    print("Exception when calling AuthApi->logout_a_user: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

[jwtkey](../README.md#jwtkey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **user_login**
> ResponseDetails user_login(payload)



### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.AuthApi()
payload = swagger_client.AuthDetails() # AuthDetails | 

try:
    api_response = api_instance.user_login(payload)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthApi->user_login: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **payload** | [**AuthDetails**](AuthDetails.md)|  | 

### Return type

[**ResponseDetails**](ResponseDetails.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

