# DocuMind Test Cases

This document outlines the test cases for the DocuMind application. These tests cover various aspects of the application, including API endpoints, services, and frontend components.

## API Tests

### Authentication Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| AUTH-01 | User Registration | 1. Send POST request to `/api/v1/auth/register` with valid user data | User is created and returned with 201 status code |
| AUTH-02 | User Registration - Duplicate Username | 1. Register a user<br>2. Try to register another user with the same username | 400 Bad Request with error message |
| AUTH-03 | User Registration - Duplicate Email | 1. Register a user<br>2. Try to register another user with the same email | 400 Bad Request with error message |
| AUTH-04 | User Login - Valid Credentials | 1. Register a user<br>2. Login with valid credentials | JWT token is returned with 200 status code |
| AUTH-05 | User Login - Invalid Credentials | 1. Try to login with invalid credentials | 401 Unauthorized with error message |
| AUTH-06 | Get Current User | 1. Login a user<br>2. Send GET request to `/api/v1/auth/me` with JWT token | User data is returned with 200 status code |
| AUTH-07 | Get Current User - Invalid Token | 1. Send GET request to `/api/v1/auth/me` with invalid JWT token | 401 Unauthorized with error message |

### Document Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| DOC-01 | Upload PDF | 1. Login a user<br>2. Upload a PDF file | Document is created and returned with 201 status code |
| DOC-02 | Upload PDF - Invalid File | 1. Login a user<br>2. Upload a non-PDF file | 400 Bad Request with error message |
| DOC-03 | Add Web Article | 1. Login a user<br>2. Add a web article with valid URL | Document is created and returned with 201 status code |
| DOC-04 | Add Web Article - Invalid URL | 1. Login a user<br>2. Add a web article with invalid URL | 500 Internal Server Error with error message |
| DOC-05 | Get User Documents | 1. Login a user<br>2. Upload multiple documents<br>3. Send GET request to `/api/v1/documents` | List of documents is returned with 200 status code |
| DOC-06 | Get Document | 1. Login a user<br>2. Upload a document<br>3. Send GET request to `/api/v1/documents/{document_id}` | Document is returned with 200 status code |
| DOC-07 | Get Document - Not Found | 1. Login a user<br>2. Send GET request to `/api/v1/documents/{invalid_document_id}` | 404 Not Found with error message |
| DOC-08 | Get Document - Unauthorized | 1. Login user A<br>2. Upload a document as user A<br>3. Login user B<br>4. Try to access user A's document | 403 Forbidden with error message |

### Chat Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| CHAT-01 | Create Chat Session | 1. Login a user<br>2. Upload a document<br>3. Create a chat session | Chat session is created and returned with 200 status code |
| CHAT-02 | Query Document | 1. Login a user<br>2. Upload a document<br>3. Create a chat session<br>4. Send a query | Response is returned with 200 status code |
| CHAT-03 | Query Document - Invalid Document | 1. Login a user<br>2. Send a query with invalid document ID | 404 Not Found with error message |
| CHAT-04 | Query Document - Unauthorized | 1. Login user A<br>2. Upload a document as user A<br>3. Login user B<br>4. Try to query user A's document | 403 Forbidden with error message |
| CHAT-05 | Reset Chat Session | 1. Login a user<br>2. Create a chat session<br>3. Send multiple queries<br>4. Reset the chat session | Chat session is reset and returned with 200 status code |

### Highlight Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| HIGH-01 | Create Highlight | 1. Login a user<br>2. Upload a document<br>3. Create a highlight | Highlight is created and returned with 201 status code |
| HIGH-02 | Create Highlight - Invalid Document | 1. Login a user<br>2. Create a highlight with invalid document ID | 404 Not Found with error message |
| HIGH-03 | Create Highlight - Unauthorized | 1. Login user A<br>2. Upload a document as user A<br>3. Login user B<br>4. Try to create a highlight for user A's document | 403 Forbidden with error message |
| HIGH-04 | Get Smart Highlight | 1. Login a user<br>2. Send text for smart highlighting | Smart highlight is returned with 200 status code |
| HIGH-05 | Get User Highlights | 1. Login a user<br>2. Create multiple highlights<br>3. Send GET request to `/api/v1/highlights` | List of highlights is returned with 200 status code |
| HIGH-06 | Get Document Highlights | 1. Login a user<br>2. Upload a document<br>3. Create multiple highlights for the document<br>4. Send GET request to `/api/v1/highlights/document/{document_id}` | List of highlights is returned with 200 status code |
| HIGH-07 | Delete Highlight | 1. Login a user<br>2. Create a highlight<br>3. Delete the highlight | 204 No Content status code |
| HIGH-08 | Delete Highlight - Not Found | 1. Login a user<br>2. Try to delete a non-existent highlight | 404 Not Found with error message |

### Summary Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| SUM-01 | Generate Document Summary | 1. Login a user<br>2. Upload a document<br>3. Generate a summary | Summary is returned with 200 status code |
| SUM-02 | Generate Document Summary - Invalid Document | 1. Login a user<br>2. Generate a summary with invalid document ID | 404 Not Found with error message |
| SUM-03 | Generate Document Summary - Unauthorized | 1. Login user A<br>2. Upload a document as user A<br>3. Login user B<br>4. Try to generate a summary for user A's document | 403 Forbidden with error message |
| SUM-04 | Generate Semantic Summary | 1. Login a user<br>2. Create multiple highlights<br>3. Generate a semantic summary | Semantic summary is returned with 200 status code |

### Study Guide Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| STU-01 | Generate Study Guide | 1. Login a user<br>2. Upload a document<br>3. Generate a study guide | Study guide is returned with 200 status code |
| STU-02 | Generate Study Guide - Invalid Document | 1. Login a user<br>2. Generate a study guide with invalid document ID | 404 Not Found with error message |
| STU-03 | Generate Study Guide - Unauthorized | 1. Login user A<br>2. Upload a document as user A<br>3. Login user B<br>4. Try to generate a study guide for user A's document | 403 Forbidden with error message |

## Service Tests

### VectorDB Service Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| VDB-01 | Add Document | 1. Create document chunks<br>2. Add to vector database | Document is added and chunk count is returned |
| VDB-02 | Add PDF | 1. Create a PDF file<br>2. Add to vector database | Document is added and chunk count is returned |
| VDB-03 | Add Web Article | 1. Provide a valid URL<br>2. Add to vector database | Document is added and metadata is returned |
| VDB-04 | Query | 1. Add a document<br>2. Query the vector database | Relevant documents are returned |
| VDB-05 | Hybrid Query | 1. Add a document<br>2. Perform a hybrid query | Relevant documents are returned |
| VDB-06 | Get Documents | 1. Add a document<br>2. Get all documents | List of documents is returned |

### LLM Service Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| LLM-01 | Generate RAG Response | 1. Provide a query and context<br>2. Generate a response | Response is returned |
| LLM-02 | Generate Smart Highlight | 1. Provide text<br>2. Generate a smart highlight | Smart highlight is returned |
| LLM-03 | Generate Semantic Summary | 1. Provide highlights<br>2. Generate a semantic summary | Semantic summary is returned |
| LLM-04 | Generate Study Guide | 1. Provide document chunks<br>2. Generate a study guide | Study guide is returned |

## Frontend Tests

### Authentication UI Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| UI-AUTH-01 | Login Form | 1. Open the application<br>2. Enter valid credentials<br>3. Click Login | User is logged in and redirected to the main page |
| UI-AUTH-02 | Login Form - Invalid Credentials | 1. Open the application<br>2. Enter invalid credentials<br>3. Click Login | Error message is displayed |
| UI-AUTH-03 | Register Form | 1. Open the application<br>2. Click Register tab<br>3. Enter valid user data<br>4. Click Register | Success message is displayed |
| UI-AUTH-04 | Logout | 1. Login a user<br>2. Click Logout | User is logged out and redirected to the login page |

### Document UI Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| UI-DOC-01 | Upload PDF | 1. Login a user<br>2. Upload a PDF file<br>3. Click Process PDF | Success message is displayed and document is added to the list |
| UI-DOC-02 | Add Web Article | 1. Login a user<br>2. Enter a valid URL<br>3. Click Process URL | Success message is displayed and document is added to the list |
| UI-DOC-03 | Document List | 1. Login a user<br>2. Upload multiple documents | Documents are displayed in the sidebar |
| UI-DOC-04 | Select Document | 1. Login a user<br>2. Upload a document<br>3. Click on the document in the sidebar | Document is selected and displayed in the main area |

### Chat UI Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| UI-CHAT-01 | Chat Interface | 1. Login a user<br>2. Select a document<br>3. Enter a query<br>4. Press Enter | Response is displayed in the chat interface |
| UI-CHAT-02 | Chat History | 1. Login a user<br>2. Select a document<br>3. Send multiple queries | Chat history is displayed in the chat interface |
| UI-CHAT-03 | Reset Chat | 1. Login a user<br>2. Select a document<br>3. Send multiple queries<br>4. Click Reset Chat | Chat history is cleared |

### Highlight UI Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| UI-HIGH-01 | Create Highlight | 1. Login a user<br>2. Select a document<br>3. Enter text to highlight<br>4. Click Generate Smart Highlight | Smart highlight is displayed |
| UI-HIGH-02 | Save Highlight | 1. Login a user<br>2. Select a document<br>3. Generate a smart highlight<br>4. Click Save Highlight | Success message is displayed and highlight is added to the list |
| UI-HIGH-03 | Document Highlights | 1. Login a user<br>2. Select a document<br>3. Create multiple highlights | Highlights are displayed in the highlights tab |

### Summary UI Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| UI-SUM-01 | Generate Summary | 1. Login a user<br>2. Select a document<br>3. Click Generate Summary | Summary is displayed in the summary tab |

### Study Guide UI Tests

| Test ID | Description | Steps | Expected Result |
|---------|-------------|-------|----------------|
| UI-STU-01 | Generate Study Guide | 1. Login a user<br>2. Select a document<br>3. Click Generate Study Guide | Study guide is displayed in the study guide tab |
| UI-STU-02 | Key Concepts | 1. Login a user<br>2. Select a document<br>3. Generate a study guide<br>4. Click Key Concepts | Key concepts are displayed |
| UI-STU-03 | Review Questions | 1. Login a user<br>2. Select a document<br>3. Generate a study guide<br>4. Click Review Questions | Review questions are displayed |
