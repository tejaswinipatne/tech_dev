/**
 * jQuery serializeObject
 * Serializes a form (or a set of inputs) to an object. It uses FileReader and Deferred to serialize input[type="file"]
 * @returns {jQuery.Deferred} deferred object
 * @requires jQuery 1.5+
 * @requires FileReader JavaScript API
 * @author Aleksandr.ru
 * @link http://aleksandr.ru
 * 
 * @link http://stackoverflow.com/questions/1184624/convert-form-data-to-javascript-object-with-jquery
 * @link https://www.html5rocks.com/ru/tutorials/file/dndfiles/
 * @link http://stackoverflow.com/questions/6978156/get-base64-encode-file-data-from-input-form
 */
;(function($) {
	if (window.File && window.FileReader && window.FileList && $.Deferred)
	$.fn.serializeObject = function() {
		var $form = $(this);
		return $.when().then(function() {
			var defer = new $.Deferred();

			var a = $form.find(':input[name]').not(':checkbox').serializeArray();
			$form.find(':checkbox[name]').each(function() {
				if(this.hasAttribute('value')) {
					if(this.checked) a.push({
						name: this.name,
						value: this.value
					});
				}
				else a.push({
					name: this.name,
					value: this.checked
				});
			});
			defer.resolve(a);

			return defer.promise();
		}).then(function(a){
			var defer = new $.Deferred();

			var defers = [], readers = [];
			$form.find('input[type="file"][name]').each(function() {
				var input = $(this).get(0);
				for (var i = 0; i < input.files.length; i++) {
					defers.push(new $.Deferred());
					readers.push(new FileReader());

					var k = defers.length - 1;
					readers[k].onload = (function(file, defer, inputName) {
						return function(e) {							
							var dataURL = e.target.result;
							var pos = dataURL.indexOf(',') + 1;
							var fo = {
								name: file.name,
								type: file.type,
								size: file.size,
								data: pos ? dataURL.slice(pos) : null
							};							
							defer.resolve({
								name: inputName,
								value: fo
							});
						};
					})(input.files[i], defers[k], input.name);

					readers[k].onerror = (function(defer) {
						return function(e) {
							defer.reject(e.target.error);
						};
					})(defers[k]);

					readers[k].readAsDataURL(input.files[i]);
				}
			});
			$.when.apply($, defers).then(function() {
				if(arguments[0]) for(var i = 0; i < arguments.length; i++) a.push(arguments[i]);
				defer.resolve(a);
			}, function(e) {
				defer.reject(e);
			});

			return defer.promise();
		}).then(function(a) {
			var defer = new $.Deferred();

			var o = {};
			$.each(a, function() {
				var val = this.value === undefined ? '' : this.value;
				if (this.name.slice(-2) === '[]'){ // force array
					this.name = this.name.slice(0, -2);
					if (o[this.name] === undefined) o[this.name] = [];
				}
				if (o[this.name] !== undefined) {
					if (!o[this.name].push) {
						o[this.name] = [o[this.name]];
					}
					o[this.name].push(val);
				}
				else {
					o[this.name] = val;
				}
			});
			defer.resolve(o);

			return defer.promise();
		});
	};
})(jQuery);