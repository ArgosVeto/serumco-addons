odoo.define('website_argos.resume_upload', function(require) {
	$(document).ready(function() {

	var rpc = require('web.rpc');
	var ajax = require('web.ajax');
	$('#resume_file1').change(get_File1_Upload);

	function get_File1_Upload()
	{
		var image_input = null;
		var self = this;
		var resume_file1 = document.querySelector('#resume_file1').files[0];
		if (resume_file1) {
			var reader1 = new FileReader();
			reader1.readAsDataURL(resume_file1);
			reader1.onload = function(e){
				image_input = e.target.result;
				ajax.rpc('/job/resume-attachment',{'file_upload1':image_input,'file_name':resume_file1.name,'mimetype':resume_file1.type}).then(function(data){
					$("#div_file1").val(data);
				});
			}				
			}
		}

	})
})