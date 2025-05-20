export type Method = 'GET' | 'POST' | 'PUT' | 'DELETE'

export const APIFetch = async (urlPath:string, idToken:string, body?:string, method?:Method) => {
    const response = await fetch(`/api/${urlPath}`, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${idToken}`
        },
        body: body
        
      });
    return await response.json()
}
