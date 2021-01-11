odoo.define('website_argos.resume_upload', function(require) {
	$(document).ready(function() {

	var rpc = require('web.rpc');
	var ajax = require('web.ajax');
	$('#resume_file1').change(get_File1_Upload);
	$('#resume_file2').change(get_File2_Upload);

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
				ajax.rpc('/job/resume-attachment',{'file_upload':image_input,'file_name':resume_file1.name,'mimetype':resume_file1.type}).then(function(data){
					$("#div_file1").val(data);
				});
			}				
			}
		}
	function get_File2_Upload()
		{
			var image_input = null;
			var self = this;
			var resume_file2 = document.querySelector('#resume_file2').files[0];
			if (resume_file2) {
				var reader2 = new FileReader();
				reader2.readAsDataURL(resume_file2);
				reader2.onload = function(e){
					image_input = e.target.result;
					ajax.rpc('/job/resume-attachment',{'file_upload':image_input,'file_name':resume_file2.name,'mimetype':resume_file2.type}).then(function(data){
						$("#div_file2").val(data);
					});
				}				
				}
			}
	
	})
})