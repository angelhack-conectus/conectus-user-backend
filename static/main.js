
window.addEventListener('load', function() {
    let val = null;
    selectorList.inputMessage.addEventListener('keypress', function(e) {
        if (e.keyCode === 13) {
            val = this.value;
            if ( val ) {
                new handleMessage({
                    text: val,
                    isLeft : false
                }).draw()
                  .scrollToTop()
                  .clear();
            }

        }
    });

    selectorList.inputMessage.parentElement.nextElementSibling.addEventListener('click', function(e){
        val = selectorList.inputMessage.value;
        if (selectorList.inputMessage.value) {
            new handleMessage({
                text: val,
                isLeft: true
            }).draw()
              .scrollToTop()
              .clear();
        }
    });


});