class handleMessage {
    constructor (getObj) {
        this.text = getObj.text;
        this.isLeft = getObj.isLeft ? 'left' : 'right';
        
        this.messageTemplate = `
        <li class="message ${this.isLeft} appeared">
            <div class="avatar"></div>
            <div class="text_wrapper">
                <div class="text">${this.text}</div>
            </div>
        </li>`;
    }
    
    draw() {
        
        selectorList.message[0].insertAdjacentHTML('beforeend',this.messageTemplate);
        return this;
    }
    
    scrollToTop() {
        selectorList.message[0].scrollTo(0, selectorList.message[0].scrollHeight)
        return this;
    }

    clear() {
        selectorList.inputMessage.value = '';
    }
}