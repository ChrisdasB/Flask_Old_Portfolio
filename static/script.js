window.onload = function () {

    var username_input = document.getElementById("username");
    var username_info = document.getElementById("username-info");
    
    username_input.addEventListener("focus", function() {
        username_info.classList.remove("invisible")
        });

        username_input.addEventListener("focusout", function() {
            username_info.classList.add("invisible")
            });


    var password_input = document.getElementById("password");
    var password_info = document.getElementById("password-info");
    
    password_input.addEventListener("focus", function() {
        password_info.classList.remove("invisible")
        });

        password_input.addEventListener("focusout", function() {
            password_info.classList.add("invisible")
            });

    var password2_input = document.getElementById("password2");
    var password2_info = document.getElementById("password2-info");
    
    password2_input.addEventListener("focus", function() {
        password2_info.classList.remove("invisible")
        });

        password2_input.addEventListener("focusout", function() {
            password2_info.classList.add("invisible")
            });
};



