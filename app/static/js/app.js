const ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws');
ws.addEventListener('open', () => console.log('ws open'));
ws.addEventListener('message', (ev) => {
  try{
    const data = JSON.parse(ev.data);
    if(data.type === 'price_update'){
      document.querySelector('[x-data]').__x.$data.symbol = data.symbol;
      document.querySelector('[x-data]').__x.$data.price = data.price;
    }
  }catch(e){
    // ignore
  }
});
