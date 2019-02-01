/*

prototypes of added function :
function (JSON_object, server_object){
    idiomatic way of sending message is :
    server_object.send_command('name_of_the_command', {
        name_of_param : value
        
        IE: 
        login : login,
        password : password
    })
}

added func will be called when a message with the 'type' field equal 
to their name is received
IE :
on auth the server will respond with a message of type auth :
thus if we do :
const auth = (js, serv) => console.log('authentified');
server.add_func(auth);

authentified will be printed automatically on auth

you can specify the name of the type if you want using the second arg

*/



class WebsocketedCon {
    constructor(adrr, params = {}, funcs = {}) {
        this.websocket = null;
        this.login = params.login;
        this.password = params.password;
        if (!this.login && !this.password) throw new Error('No password/login provided');

        this.adrr = adrr;
        this.funcs = funcs;
        if (funcs.auth === undefined) this.funcs.auth = (ws, js) => console.log('connected');

        this.onOpen = funcs.onOpen || (() => {
            console.log('opened');
            this._login(); // auto login on open
        });

        this.onClose = funcs.onClose || (() => {
            console.log('closed');
        });

        this.onError = funcs.onError || (evt => {
            console.log('error =>', evt.data);
            evt.target.close();
        });

        this.onMessage = (evt) => {
            const js = JSON.parse(evt.data);
            if (js.type === 'error') return alert(js.error || 'error {reason unknown}');
            this.funcs[js.type](js, this);
        };
    }

    _login(login, password) {
        this.send_command('auth', { login: login || this.login, password: password || this.password }); // auto login
    }

    add_func(func, name) {
        this.funcs[name || func.name] = func;
    }

    send_command(command, params={}) {
        params.type = command;
        this.websocket.send(JSON.stringify(params));
    }

    start() {
        console.log(this);
        this.websocket = new WebSocket(this.adrr);
        this.websocket.onopen = evt => this.onOpen(evt)
        this.websocket.onclose = evt => this.onClose(evt);
        this.websocket.onmessage = evt => this.onMessage(evt);
        this.websocket.onerror = evt => this.onError(evt);
    }
}
