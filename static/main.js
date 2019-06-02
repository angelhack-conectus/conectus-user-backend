(function () {
    var Message;
    Message = function (arg) {
        this.text = arg.text, this.message_side = arg.message_side;
        this.draw = function (_this) {
            return function () {
                var $message;
                $message = $($('.message_template').clone().html());
                $message.addClass(_this.message_side).find('.text').html(_this.text);
                $('.messages').append($message);
                return setTimeout(function () {
                    return $message.addClass('appeared');
                }, 0);
            };
        }(this);
        return this;
    };

    $(function () {

        let geo = null;

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((pos) => {
                geo = [
                    pos.coords.latitude, ',', pos.coords.longitude
                ].join('');
            });
        }

        var getMessageText, message_side, sendMessage;
        getMessageText = function () {
            var $message_input;
            $message_input = $('.message_input');
            return $message_input.val();
        };
        sendMessage = function (text, isMe) {
            var $messages, message;
            if (text.trim() === '') {
                return;
            }
            $('.message_input').val('');
            $messages = $('.messages');
            message_side = isMe ? 'left' : 'right';
            message = new Message({
                text: text,
                message_side: message_side
            });
            message.draw();

            return $messages.animate({
                scrollTop: $messages.prop('scrollHeight')
            }, 300);
        };

        let tmp = null;
        const getUUID = () => {
            const getRandString = () => ((1 + Math.random()) * 0x10000 | 0).toString(16)
                .substring(1);
            return [
                getRandString(), getRandString(),
                '-', getRandString(),
                '-', getRandString(),
                '-', getRandString(),
                '-', getRandString(),
                getRandString(),
                getRandString()
            ].join('');
        };

        const generateData = () => {
            

            let dummy = {
                "sequence_id": getUUID(),
                "type": "query",
                "query_type": "info",
                "my_info": {
                    "battery": null,
                    "is_online": navigator.onLine,
                    "gps": geo
                }
            };
            
            if (!dummy.my_info.gps) {
                dummy.my_info.gps = "37.495470,127.038855";
            }
            return dummy;
        };
        
        const url = 'ws://192.168.137.1:8080/websocket';
        const ws = new WebSocket(url);
        
        ws.addEventListener('open', function () {
            let data = generateData();
            let message = null;
            ws.send(JSON.stringify({
                "sequence_id": data.sequence_id,
                "type": "client_info"
            }));

            setInterval(() => {
                ws.send('ping');
            }, 1000);
            
            $('.send_message').on('click', function (e) {
                message = getMessageText();
                if (message !== '') {

                    ws.send(JSON.stringify({
                        "sequence_id": getUUID(),
                        "type": "msg",
                        "target": "general",
                        "msg": message
                    }));
                    sendMessage(message, false);
                }
                // return sendMessage(getMessageText());
            });
            $('.message_input').on('keypress',function (e) {
                if (e.keyCode === 13) {
                
                    message = getMessageText();
                    ws.send(JSON.stringify({
                        "sequence_id": getUUID(),
                        "type": "msg",
                        "target": "general",
                        "msg": message
                    }));
                    sendMessage(message, false);
                }
            });
            
            ws.addEventListener('message', function (resp) {
                const isIos = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
                if (resp.isTrusted) {
                    data = JSON.parse(resp.data);
                    let genData = generateData();
                    
                    if (data.mac) {
                        localStorage.setItem('mac', data.mac);
                        let getD = {
                            "type": "update",
                            'id': localStorage.getItem('mac'),
                            'sequence_id': getUUID(),
                            'battery': null,
                            'connected_host': data.connected_host,
                            'is_online': navigator.onLine,
                            'gps': genData.my_info.gps
                        };
                        
                        if (!isIos) {
                            (async (nav) => {
                                const bet = await nav.getBattery();
                                getD.battery = bet.level * 100;
                                ws.send(JSON.stringify(getD));
                            })(navigator);
                        } else {
                            ws.send(JSON.stringify(getD))
                        }
                    } else if (data.msg) {
                        if (data.from !== localStorage.getItem('mac')) {
                            sendMessage(data.msg, true);
                        }
                    }
                }
            });

        });
    });
}.call(this));