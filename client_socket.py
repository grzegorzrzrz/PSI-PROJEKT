import asyncio
import socketio

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print('connection established')
    await sio.emit('add-torrent', {'torrent': data, 'seeder': data1})

@sio.event
async def disconnect():
    print('disconnected from server')
    await sio.disconnect()

async def myDisconnect(a):
    await sio.disconnect()

async def main():
    await sio.connect('http://localhost:3001')
    await sio.wait()
sio.on('list-state-from-server', myDisconnect)

if __name__ == '__main__':
    asyncio.run(main())