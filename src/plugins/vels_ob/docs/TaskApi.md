# swagger_client.TaskApi

All URIs are relative to *https://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_a_new_task**](TaskApi.md#create_a_new_task) | **POST** /task/ | Creates a new Task
[**delete_a_task**](TaskApi.md#delete_a_task) | **DELETE** /task/{user_id} | delete a task given its identifier
[**get_a_bit**](TaskApi.md#get_a_bit) | **GET** /task/bit/{user_id} | get a tasks bit file given its identifier
[**get_a_task**](TaskApi.md#get_a_task) | **GET** /task/{user_id} | get a task given its identifier
[**list_of_tasks**](TaskApi.md#list_of_tasks) | **GET** /task/ | List all registered tasks
[**set_a_task_inactive**](TaskApi.md#set_a_task_inactive) | **POST** /task/inactive/{user_id} | set a task inactive given its identifier


# **create_a_new_task**
> create_a_new_task(user_id, file)

Creates a new Task

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.TaskApi()
user_id = 'user_id_example' # str | 
file = '/path/to/file.txt' # file | 

try:
    # Creates a new Task
    api_instance.create_a_new_task(user_id, file)
except ApiException as e:
    print("Exception when calling TaskApi->create_a_new_task: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**|  | 
 **file** | **file**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_a_task**
> delete_a_task(user_id)

delete a task given its identifier

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
api_instance = swagger_client.TaskApi(swagger_client.ApiClient(configuration))
user_id = 'user_id_example' # str | The Task identifier

try:
    # delete a task given its identifier
    api_instance.delete_a_task(user_id)
except ApiException as e:
    print("Exception when calling TaskApi->delete_a_task: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| The Task identifier | 

### Return type

void (empty response body)

### Authorization

[jwtkey](../README.md#jwtkey)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_a_bit**
> get_a_bit(user_id)

get a tasks bit file given its identifier

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.TaskApi()
user_id = 'user_id_example' # str | The Task identifier

try:
    # get a tasks bit file given its identifier
    api_instance.get_a_bit(user_id)
except ApiException as e:
    print("Exception when calling TaskApi->get_a_bit: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| The Task identifier | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_a_task**
> Task get_a_task(user_id, x_fields=x_fields)

get a task given its identifier

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.TaskApi()
user_id = 'user_id_example' # str | The Task identifier
x_fields = 'x_fields_example' # str | An optional fields mask (optional)

try:
    # get a task given its identifier
    api_response = api_instance.get_a_task(user_id, x_fields=x_fields)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TaskApi->get_a_task: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| The Task identifier | 
 **x_fields** | **str**| An optional fields mask | [optional] 

### Return type

[**Task**](Task.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_of_tasks**
> list[Task] list_of_tasks(x_fields=x_fields)

List all registered tasks

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.TaskApi()
x_fields = 'x_fields_example' # str | An optional fields mask (optional)

try:
    # List all registered tasks
    api_response = api_instance.list_of_tasks(x_fields=x_fields)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TaskApi->list_of_tasks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_fields** | **str**| An optional fields mask | [optional] 

### Return type

[**list[Task]**](Task.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_a_task_inactive**
> set_a_task_inactive(user_id)

set a task inactive given its identifier

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.TaskApi()
user_id = 'user_id_example' # str | The Task identifier

try:
    # set a task inactive given its identifier
    api_instance.set_a_task_inactive(user_id)
except ApiException as e:
    print("Exception when calling TaskApi->set_a_task_inactive: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| The Task identifier | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

