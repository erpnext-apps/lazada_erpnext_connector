// Copyright (c) 2020, Raaj Tailor and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lazada Settings', {
	// refresh: function(frm) {

	// }
	from_date:function(frm){
		if(frm.doc.from_date && frm.doc.to_date){
			check_date(frm.doc.from_date,frm.doc.to_date)
		}
		
	},
	to_date:function(frm){
		if(frm.doc.from_date && frm.doc.to_date){
			check_date(frm.doc.from_date,frm.doc.to_date)
		}
	},
	authorize_lazada:function(frm){
		var auth_url = "https://auth.lazada.com/oauth/authorize?response_type=code&force_auth=true&redirect_uri="+frm.doc.callback_url+"&client_id="+frm.doc.api_key
		console.log(location.origin)
		window.open(auth_url);
	}
});

function check_date(from_date,to_date){
	if(from_date > to_date){
		frappe.throw("Please Enter Correct <b>From Date</b> and <b>To Date</b>!")
	}
}
