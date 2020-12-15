var jsElm = document.createElement("script");
    jsElm.type = "application/javascript";
    jsElm.src = "//laz-g-cdn.alicdn.com/sj/securesdk/0.0.3/securesdk_lzd_v1.js";
    jsElm.id = "J_secure_sdk_v2";
    jsElm.setAttribute("data-appkey", "120609")
    
$( document ).ready(function() {
    var code = getUrlParameter('code');
    if(code){
        frappe.db.set_value("Lazada Settings",null,"code",code).then((res)=>{
            if(res.message.code){
                frappe.msgprint("Lazada is Authorized Sucessfully!")
                // window.location = window.location.href.split("?")[0];
                window.location.replace(window.location.href.split("?")[0]);
            }
        })
    }
    document.body.appendChild(jsElm);
});

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
};   