# Security Considerations

## Debug Mode Security Considerations and Warning

This library includes a debug mode feature that generates complete cURL commands
for troubleshooting API requests. This feature is designed to help during
development and debugging only.

When you enable debug mode by setting `debug=True` in any API method call:

```python
# This will print a complete curl command to stdout
client.get_profile(debug=True)
```

The generated cURL command includes:

- The full API endpoint URL
- All request parameters and data
- The OAuth bearer token used for authentication

**WARNING: This exposes sensitive authentication credentials that could allow
API access as the authenticated user.**

1. **NEVER use debug mode in production environments**
2. **NEVER log debug mode output to persistent storage**
3. **NEVER share debug mode output without removing the authorization token**
4. **NEVER commit debug mode output to version control**

## General Security Considerations

### OAuth Token Management

- Store OAuth tokens securely, preferably in an encrypted format
- Implement token rotation and refresh mechanisms properly
- Never hard-code tokens in application code
- Use environment variables or secure configuration management for client IDs
  and secrets

### Production Deployment

- Ensure token refresh callbacks use HTTPS
- Validate that your callback URL is properly secured
- Follow OAuth 2.0 best practices for authentication flows
- Set appropriate token expiration times
