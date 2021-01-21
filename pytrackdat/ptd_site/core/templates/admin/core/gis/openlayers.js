/*
Portions copyright (c) Django Software Foundation and individual contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Django nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Portions copyright (C) 2018-2020 the PyTrackDat authors.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact information:
    David Lougheed (david.lougheed@gmail.com)
 */

{% load l10n %}
OpenLayers.Projection.addTransform("EPSG:4326", "EPSG:3857", OpenLayers.Layer.SphericalMercator.projectForward);
{% block vars %}var {{ module }} = {};
{{ module }}.map = null; {{ module }}.controls = null; {{ module }}.panel = null; {{ module }}.re = new RegExp("^SRID=\\d+;(.+)", "i"); {{ module }}.layers = {};
{{ module }}.modifiable = {{ modifiable|yesno:"true,false" }};
{{ module }}.wkt_f = new OpenLayers.Format.WKT();
{{ module }}.is_collection = {{ is_collection|yesno:"true,false" }};
{{ module }}.collection_type = '{{ collection_type }}';
{{ module }}.is_generic = {{ is_generic|yesno:"true,false" }};
{{ module }}.is_linestring = {{ is_linestring|yesno:"true,false" }};
{{ module }}.is_polygon = {{ is_polygon|yesno:"true,false" }};
{{ module }}.is_point = {{ is_point|yesno:"true,false" }};
{% endblock %}
{{ module }}.get_ewkt = function(feat){
    return 'SRID={{ srid|unlocalize }};' + {{ module }}.wkt_f.write(feat);
};
{{ module }}.read_wkt = function(wkt){
    // OpenLayers cannot handle EWKT -- we make sure to strip it out.
    // EWKT is only exposed to OL if there's a validation error in the admin.
    var match = {{ module }}.re.exec(wkt);
    if (match){wkt = match[1];}
    return {{ module }}.wkt_f.read(wkt);
};
{{ module }}.write_wkt = function(feat){
    if ({{ module }}.is_collection){ {{ module }}.num_geom = feat.geometry.components.length;}
    else { {{ module }}.num_geom = 1;}
    document.getElementById('{{ id }}').value = {{ module }}.get_ewkt(feat);
    {{ module }}.write_human(feat);
};
{{ module }}.add_wkt = function(event){
    // This function will sync the contents of the `vector` layer with the
    // WKT in the text field.
    if ({{ module }}.is_collection){
        var feat = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.{{ geom_type }}());
        for (var i = 0; i < {{ module }}.layers.vector.features.length; i++){
            feat.geometry.addComponents([{{ module }}.layers.vector.features[i].geometry]);
        }
        {{ module }}.write_wkt(feat);
    } else {
        // Make sure to remove any previously added features.
        if ({{ module }}.layers.vector.features.length > 1){
            old_feats = [{{ module }}.layers.vector.features[0]];
            {{ module }}.layers.vector.removeFeatures(old_feats);
            {{ module }}.layers.vector.destroyFeatures(old_feats);
        }
        {{ module }}.write_wkt(event.feature);
    }
};
{{ module }}.modify_wkt = function(event){
    if ({{ module }}.is_collection){
        if ({{ module }}.is_point){
            {{ module }}.add_wkt(event);
            return;
        } else {
            // When modifying the selected components are added to the
            // vector layer so we only increment to the `num_geom` value.
            var feat = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.{{ geom_type }}());
            for (var i = 0; i < {{ module }}.num_geom; i++){
                feat.geometry.addComponents([{{ module }}.layers.vector.features[i].geometry]);
            }
            {{ module }}.write_wkt(feat);
        }
    } else {
        console.log(event.feature);
        {{ module }}.write_wkt(event.feature);
    }
};

// Added by David Lougheed
{{ module }}.write_human = function (feat) {
    var wkt = {{ module }}.get_ewkt(feat);
    var value = wkt.split(";")[1];

    document.getElementById('{{ id }}.srid').value = "{{ srid|unlocalize }}";
    document.getElementById('{{ id }}.value').value = value;
};

// Function to clear vector features and purge wkt from div
{{ module }}.deleteFeatures = function(){
    {{ module }}.layers.vector.removeFeatures({{ module }}.layers.vector.features);
    {{ module }}.layers.vector.destroyFeatures();
};
{{ module }}.clearFeatures = function (){
    {{ module }}.deleteFeatures();
    document.getElementById('{{ id }}').value = '';
    {% localize off %}
    {{ module }}.map.setCenter(new OpenLayers.LonLat({{ default_lon }}, {{ default_lat }}), {{ default_zoom }});
    {% endlocalize %}
};
// Add Select control
{{ module }}.addSelectControl = function(){
    var select = new OpenLayers.Control.SelectFeature({{ module }}.layers.vector, {'toggle' : true, 'clickout' : true});
    {{ module }}.map.addControl(select);
    select.activate();
};
{{ module }}.enableDrawing = function(){
    {{ module }}.map.getControlsByClass('OpenLayers.Control.DrawFeature')[0].activate();
};
{{ module }}.enableEditing = function(){
    {{ module }}.map.getControlsByClass('OpenLayers.Control.ModifyFeature')[0].activate();
};
// Create an array of controls based on geometry type
{{ module }}.getControls = function(lyr){
    {{ module }}.panel = new OpenLayers.Control.Panel({'displayClass': 'olControlEditingToolbar'});
    {{ module }}.controls = [new OpenLayers.Control.Navigation()];
    if (!{{ module }}.modifiable && lyr.features.length) return;
    if ({{ module }}.is_linestring || {{ module }}.is_generic){
        {{ module }}.controls.push(new OpenLayers.Control.DrawFeature(lyr, OpenLayers.Handler.Path, {'displayClass': 'olControlDrawFeaturePath'}));
    }
    if ({{ module }}.is_polygon || {{ module }}.is_generic){
        {{ module }}.controls.push(new OpenLayers.Control.DrawFeature(lyr, OpenLayers.Handler.Polygon, {'displayClass': 'olControlDrawFeaturePolygon'}));
    }
    if ({{ module }}.is_point || {{ module }}.is_generic){
        {{ module }}.controls.push(new OpenLayers.Control.DrawFeature(lyr, OpenLayers.Handler.Point, {'displayClass': 'olControlDrawFeaturePoint'}));
    }
    if ({{ module }}.modifiable){
        {{ module }}.controls.push(new OpenLayers.Control.ModifyFeature(lyr, {'displayClass': 'olControlModifyFeature'}));
    }
};

// Added by David Lougheed
{{ module }}.onValueChange = function (clear) {
    if (clear) {
        {{ module }}.layers.vector.removeAllFeatures();
    }
    // Read WKT from the text field.
    var wkt = document.getElementById('{{ id }}').value;
    if (wkt){
        // After reading into geometry, immediately write back to
        // WKT <textarea> as EWKT (so that SRID is included).
        var admin_geom = {{ module }}.read_wkt(wkt);
        {{ module }}.write_wkt(admin_geom);
        if ({{ module }}.is_collection){
            // If geometry collection, add each component individually so they may be
            // edited individually.
            for (var i = 0; i < {{ module }}.num_geom; i++){
                {{ module }}.layers.vector.addFeatures([new OpenLayers.Feature.Vector(admin_geom.geometry.components[i].clone())]);
            }
        } else {
            {{ module }}.layers.vector.addFeatures([admin_geom]);
        }
        // Zooming to the bounds.
        {{ module }}.map.zoomToExtent(admin_geom.geometry.getBounds());
        if ({{ module }}.is_point){
            {{ module }}.map.zoomTo({{ point_zoom }});
        }
    } else {
        {% localize off %}
        {{ module }}.map.setCenter(new OpenLayers.LonLat({{ default_lon }}, {{ default_lat }}), {{ default_zoom }});
        {% endlocalize %}
    }
}

{{ module }}.init = function(){
    {% block map_options %}// The options hash, w/ zoom, resolution, and projection settings.
    var options = {
{% autoescape off %}{% for item in map_options.items %}      '{{ item.0 }}' : {{ item.1 }}{% if not forloop.last %},{% endif %}
{% endfor %}{% endautoescape %}    };{% endblock %}
    // The admin map for this geometry field.
    {% block map_creation %}
    {{ module }}.map = new OpenLayers.Map('{{ id }}_map', options);
    // Base Layer
    {{ module }}.layers.base = {% block base_layer %}new OpenLayers.Layer.WMS("{{ wms_name }}", "{{ wms_url }}", {layers: '{{ wms_layer }}'{{ wms_options|safe }}});{% endblock %}
    {{ module }}.map.addLayer({{ module }}.layers.base);
    {% endblock %}
    {% block extra_layers %}{% endblock %}
    {% if is_linestring %}OpenLayers.Feature.Vector.style["default"]["strokeWidth"] = 3; // Default too thin for linestrings. {% endif %}
    {{ module }}.layers.vector = new OpenLayers.Layer.Vector(" {{ field_name }}");
    {{ module }}.map.addLayer({{ module }}.layers.vector);
    var wkt = document.getElementById('{{ id }}').value;
    {{ module }}.onValueChange(false);
    // This allows editing of the geographic fields -- the modified WKT is
    // written back to the content field (as EWKT, so that the ORM will know
    // to transform back to original SRID).
    {{ module }}.layers.vector.events.on({"featuremodified" : {{ module }}.modify_wkt});
    {{ module }}.layers.vector.events.on({"featureadded" : {{ module }}.add_wkt});
    document.getElementById("{{ id }}.value").addEventListener("change", function (event) {
        document.getElementById('{{ id }}').value = "SRID={{ srid|unlocalize }};" + event.target.value;
        {{ module }}.onValueChange(true);
    });
    {% block controls %}
    // Map controls:
    // Add geometry specific panel of toolbar controls
    {{ module }}.getControls({{ module }}.layers.vector);
    {{ module }}.panel.addControls({{ module }}.controls);
    {{ module }}.map.addControl({{ module }}.panel);
    {{ module }}.addSelectControl();
    // Then add optional visual controls
    {% if mouse_position %}{{ module }}.map.addControl(new OpenLayers.Control.MousePosition());{% endif %}
    {% if scale_text %}{{ module }}.map.addControl(new OpenLayers.Control.Scale());{% endif %}
    {% if layerswitcher %}{{ module }}.map.addControl(new OpenLayers.Control.LayerSwitcher());{% endif %}
    // Then add optional behavior controls
    {% if not scrollable %}{{ module }}.map.getControlsByClass('OpenLayers.Control.Navigation')[0].disableZoomWheel();{% endif %}
    {% endblock %}
    if (wkt){
        if ({{ module }}.modifiable){
            {{ module }}.enableEditing();
        }
    } else {
        {{ module }}.enableDrawing();
    }
};
