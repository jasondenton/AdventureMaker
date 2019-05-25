TEMPLATE_CATALOG = {};

function render_datadriven(tmp,docobj) {
	template = docobj.getAttribute("template");
	if (!(template in TEMPLATE_CATALOG)) {
		$.get(template + '.template', function(data, status) {
			TEMPLATE_CATALOG[template] = Handlebars.compile(data);
		});
	}
	dataurl = docobj.getAttribute("data");

	data = null;
	$.get(dataurl, function(d, status) {
		data = d;
	});

	html = TEMPLATE_CATALOG[template](data);
	previous = 'previous';

	while (html != previous) {
		previous = html;
		tfunc = Handlebars.compile(html);
		html = tfunc(data);
	}	
	docobj.innerHTML = html;
}

function main()
{
	jQuery.ajaxSetup({async:false});
	$('.datadriven').each(render_datadriven);
}

$(document).ready(main);
