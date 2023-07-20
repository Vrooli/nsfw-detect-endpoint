# Ready-to-Use NSFW Detection API
This repository contains a simple Flask API for detecting NSFW images using [this NSFW detection model](https://pypi.org/project/nsfw-detector/).

## [👩🏼‍💻 Developer setup][setup-guide]
Linked is our guide for setting up all Vrooli repos. No extra steps are required.

### Minimum requirements for Virtual Private Server (VPS)
- Memory: 2GB  
- CPUs: 1

## Usage
Send a POST request to `http://localhost:<PORT_NSFW>` if testing locally, or `https://<your-domain>` if testing on a Virtual Private Server (VPS). The request must contain the following structure:

```json
{
    "key": "<your-api-key>", // Only if API_KEY environment variable is set
    "images": [{
        "buffer": "<base64-encoded-image>",
        "hash": "<unique-hash-for-image>" // If provided, used to prevent computing for the image if it is passed again
    }]
}
```

As a curl request, it looks like this:

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -H "key: <your_api_key>" \
     -d '{"images": [{"buffer": "<base64-encoded-image>", "hash": "<unique-hash-for-image>"}]}' \
     http://localhost:<PORT_NSFW>
```

If you are authenticated, it will return an object of this shape:

```
{
    "predictions": [
        "<unique-hash-for-image>": {
            "drawings": 0.12345678,
            "hentai": 2.12121212,
            "neutral": 69.42000000,
            "porn": 1.88888888,
            "sexy": 8.76543210,
        }
    ]
}
```

## Updating the model
The model is taken from [the NSFW detection model's release page](https://github.com/GantMan/nsfw_model/releases). All you need to do is: 
1. Download the mobilenet*.zip from the latest release
2. Unzip it  
3. Copy the `.h5` for the model (not the weights!) to this repo's `models` folder

## Contributions
Contributions are always welcome! If you have suggestions for improvements, please create an issue or a pull request💖


[setup-guide]: https://docs.vrooli.com/setup/getting_started.html
