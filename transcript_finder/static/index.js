console.log("index.js is included")

const renderChannels = channels => {
    console.log("rendering");
    
    let content = '';
    channels.forEach(channel => {
        content += `<tr><td>${channel.name}</td><td>${channel.id}</td><td>${channel.video_count}</td></tr>`
    });

    document.getElementById("channel-table").innerHTML = content;
}

const getChannels = async () => {
    console.log("getting channels")
    try {
        const response = await fetch('/api/channels')
        if (response.ok) {
            const data = await response.json()
            console.log(data)
            renderChannels(data);
        }
        else
        {
            console.log('failed to fetch channels')
        }
    }
    catch (error) {
        console.log('failed to fetch channels')
    }
}

const deleteChannel = async (channelID) => {
    try {
        request = {
            method: "DELETE",
            headers: {
                'Content-Type' : 'application/json'
            }
        }
        const response = await fetch(`/api/channel/${channelID}`, request)
        if (response.ok)
        {
            console.log("Deleted channel");
            
        }
        else{
            console.log('Failed to delete channel');
            
        }
    }
    catch {
        console.log('Failed to delete channel');
    }
}

document.addEventListener('DOMContentLoaded', getChannels);