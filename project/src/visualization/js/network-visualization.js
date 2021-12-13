/*
 * File: network-visualization.js
 * Author: Vincent Chung <vwchung2@illinois.edu>
 * Course: CS519 - Scientific Visualization (Fall 2021)
 * Assingment: Course Project
 */

function redrawGraph() {
    if (network_data == null) {
        console.log("Error: network_data is null");
        return;
    }

    const data = network_data

    $("#network_graph canvas").remove();
    var cnvs = document.createElement("canvas");
    cnvs.width = $("#network_graph").width();
    cnvs.height = $("#network_graph").height();
    console.log("Drawing network graph, canvas size=(" + cnvs.width + ", " + cnvs.height +")")
    $("#network_graph").append(cnvs);

    var graph = new ccNetViz(cnvs, {
        styles: data.styles
    });

    graph.set(data.nodes, data.edges, "force").then(() => {
        graph.draw();
    });
}

function redrawLegend() {
    if (network_data == null) {
        console.log("Error: network_data is null");
        return;
    }

    const clsw = network_data.num_clsw;
    const lgnd = network_data.proto_lgnd;

    $("#legend").empty();
    // Clients + Switches
    $("#legend").append(
        "<div>" +
        "<img class=\"legend-icon\" " +
            "src=\"images/icons8-computer-64.png\" />" +
        "&nbsp;Client " +
        "(" + clsw[0] + ")" +
        "</div>"
    );
    $("#legend").append(
        "<div>" +
        "<img class=\"legend-icon\" " +
            "src=\"images/icons8-router-64_blue.png\" />" +
        "&nbsp;Switch " +
        "(" + clsw[1] + ")" +
        "</div>"
    );

    // Protocols
    for (var i = 0; i < lgnd.length; i++) {
        $("#legend").append(
            "<div>" +
            "<span class=\"lgnd_splotch\" " +
                "style=\"background-color: " + lgnd[i][0] + "\"></span>" +
            "&nbsp; " + lgnd[i][1] + " " +
            "(" + lgnd[i][2] + ")" +
            "</div>"
        );
    }
}

var graph_set = null;
var network_data = null

function loadNetworkGraph(json_url) {
    console.log("Loading network graph: " + json_url)
    $.getJSON(json_url, function(data) {
        network_data = data;
        redrawGraph();
        redrawLegend();
    });
}

function setNoFlowsSel(flow_sets, flow_idx) {
    if (graph_set == null) {
        console.log("Error: graph_set is null");
        return;
    }

    sel_label = $('#nvg-no-flows-label')
    sel_label.text(flow_sets[flow_idx].num_flows);

    sel_list = $('#nvg-no-flows-select-list');
    sel_list.empty();
    for (var i = 0; i < flow_sets.length; i++) {
        id = "nvg-no-flows-" + i;
        sel_list.append("<li><a " +
            "id=\"" + id + "\" " +
            "class=\"dropdown-item\" href=\"#\">" +
            flow_sets[i].num_flows +
            "</a></li>");

            $("#" + id).click({idx:i}, function(event) {
                sel_label.text($(this).text());
                setGraphSet(event.data.idx);
            });
    }
}

function setGraphSet(flow_idx) {
    if (graph_set == null) {
        console.log("Error: graph_set is null");
        return;
    }

    loadNetworkGraph(graph_set.flow_sets[flow_idx].fname);

    $('#nvg-no-flows-total').text(graph_set.total_flows);

    setNoFlowsSel(graph_set.flow_sets, flow_idx);
}

function drawTimeSel(timesteps) {
    for (var i = 0; i < graph_sets.length; i++) {
        gt_sel = $("#nvg-graph-time-sel");
        id = "nvg-ts-" + i;
        gt_sel.append("<input type=\"radio\" class=\"btn-check\" name=\"btnradio\"" +
            "id=\"" + id + "\" autocomplete=\"off\">")
        gt_sel.append("<label class=\"btn btn-outline-primary\" " +
            "for=\"" + id + "\">" + graph_sets[i].label + "</label>")

        $("#" + id).click({idx:i}, function(event) {
            drawGraphSet(graph_sets[event.data.idx]);
        });

        if (i == 0) {
            $('#'+id).attr("checked", true);
        }
    }
}

function drawGraphSet(gs) {
    graph_set = gs;
    setGraphSet(gs.flow_default);
}

function drawGraphSets() {
    drawTimeSel();

    // Load the default graph set
    drawGraphSet(graph_sets[0]);
}

var graph_sets = null;

function loadGraphManifest(json_url) {
    console.log("Loading graphs manifest: " + json_url)
    $.ajax({
        url: json_url,
        dataType: 'json',
        async: false,
        success: function(data) {
            graph_sets = data;
        }
    });
}

$(document).ready(function() {
    loadGraphManifest("datasets/graphs-manifest.json");
    drawGraphSets();

    $(window).resize(function() {
        redrawGraph();
    });
});
