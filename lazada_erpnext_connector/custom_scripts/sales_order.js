frappe.ui.form.on("Sales Order", {
	refresh: function(frm) {
        if(frm.doc.docstatus===1) {
            cur_frm.add_custom_button(__('Get ewaybill'), function(){
            console.log("here") 
        });
        cur_frm.add_custom_button(__('Get Transaction Details'), function(){
            frappe.call({
                "method":"",
                
            })
        });
		}
    }
})