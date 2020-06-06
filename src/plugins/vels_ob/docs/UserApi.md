# swagger_client.UserApi

All URIs are relative to *https://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_a_new_user**](UserApi.md#create_a_new_user) | **POST** /user/ | Creates a new User
[**delete_a_user**](UserApi.md#delete_a_user) | **DELETE** /user/{public_id} | delete a user given its identifier
[**get_a_user**](UserApi.md#get_a_user) | **GET** /user/{public_id} | get a user given its identifier
[**list_of_registered_users**](UserApi.md#list_of_registered_users) | **GET** /user/ | List all registered users


# **create_a_new_user**
> ResponseDetails create_a_new_user(payload, x_fields=x_fields)

Creates a new User

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.UserApi()
payload = swagger_client.User() # User | 
x_fields = 'x_fields_example' # str | An optional fields mask (optional)

try:
    # Creates a new User
    api_response = api_instance.create_a_new_user(payload, x_fields=x_fields)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UserApi->create_a_new_user: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **payload** | [**User**](User.md)|  | 
 **x_fields** | **str**| An optional fields mask | [optional] 

### Return type

[**ResponseDetails**](ResponseDetails.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_a_user**
> delete_a_user(public_id)

delete a user given its identifier

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
api_instance = swagger_client.UserApi(swagger_client.ApiClient(configuration))
public_id = 'public_id_example' # str | The User identifier

try:
    # delete a user given its identifier
    api_instance.delete_a_user(public_id)
except ApiException as e:
    print("Exception when calling UserApi->delete_a_user: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **public_id** | **str**| The User identifier | 

### Return type

void (empty response body)

### Authorization

[jwtkey](../README.md#jwtkey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_a_user**
> User get_a_user(public_id, x_fields=x_fields)

get a user given its identifier

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.UserApi()
public_id = 'public_id_example' # str | The User identifier
x_fields = 'x_fields_example' # str | An optional fields mask (optional)

try:
    # get a user given its identifier
    api_response = api_instance.get_a_user(public_id, x_fields=x_fields)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UserApi->get_a_user: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **public_id** | **str**| The User identifier | 
 **x_fields** | **str**| An optional fields mask | [optional] 

### Return type

[**User**](User.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_of_registered_users**
> list[User] list_of_registered_users(x_fields=x_fields)

List all registered users

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
api_instance = swagger_client.UserApi(swagger_client.ApiClient(configuration))
x_fields = 'x_fields_example' # str | An optional fields mask (optional)

try:
    # List all registered users
    api_response = api_instance.list_of_registered_users(x_fields=x_fields)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UserApi->list_of_registered_users: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_fields** | **str**| An optional fields mask | [optional] 

### Return type

[**list[User]**](User.md)

### Authorization

[jwtkey](../README.md#jwtkey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

