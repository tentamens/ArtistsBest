import base64

client_id = '92a2dede3a44403ab62b7b38138c861b'
client_secret = '4951963c88db452da9c28003372b218e'

authOptions = {
    'url': 'https://accounts.spotify.com/api/token',
    'headers': { 'Authorization': 'Basic ' + base64.b64encode((client_id + ':' + client_secret).encode()).decode() },
    'form': { 'grant_type': 'client_credentials' },
    'json': True
}