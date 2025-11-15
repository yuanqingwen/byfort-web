(async ()=>{
  const chat = document.getElementById('chat')
  const q = document.getElementById('q')
  const send = document.getElementById('send')

  // create device id in localStorage
  let deviceId = localStorage.getItem('byfort_device')
  if(!deviceId){
    deviceId = 'd'+Math.random().toString(36).slice(2,12)
    localStorage.setItem('byfort_device', deviceId)
  }

  // call device-login
  const r = await fetch('/api/auth/device-login',{method:'POST',headers:{'X-Device-ID':deviceId}})
  const j = await r.json()
  const token = j.token

  // WebSocket
  const ws = new WebSocket((location.protocol==='https:'?'wss':'ws')+'://'+location.host+'/ws?token='+token)
  ws.onmessage = (ev)=>{
    try{const d = JSON.parse(ev.data); const el = document.createElement('div'); el.textContent = JSON.stringify(d); chat.appendChild(el); chat.scrollTop = chat.scrollHeight;}catch(e){}
  }

  send.onclick = async ()=>{
    const text = q.value.trim(); if(!text) return;
    // send to /api/chat/send
    await fetch('/api/chat/send',{method:'POST',headers:{'Content-Type':'application/json','Authorization':token},body:JSON.stringify({to:'server',text})})
    // send to ws to store & get echo
    ws.send(JSON.stringify({to:'server',text}))
    q.value=''
  }
})()
