'use strict';
// customized script to draw the amount of agent through each exit

var BarChartModule = function(fields, canvas_width, canvas_height, sorting, sortingKey) {
    // Create the overall chart div
    var chart_div_tag = "<div class='bar chart' width='" + canvas_width + "'></div>";
    var chart_div = $(chart_div_tag)[0];
    $("#elements").append(chart_div);

    // Create the tag:
    var svg_tag = "<svg width='" + canvas_width + "' height='" + canvas_height + "' ";
    svg_tag += "style='border:1px solid; padding-left:10px; margin-bottom:30px'></svg>";
    // Append it to #elements
    var svg_element = $(svg_tag)[0];
    chart_div.append(svg_element);

    var categories = ["Exit (0, 5)", "Exit (0, 25)", "Exit (0, 45)", "Exit (49, 14)", "Exit (49, 15)", "Exit (49, 16)"]


    // setup the d3 svg selection
    var svg = d3.select(svg_element)
    var margin = {top: 80, right: 20, bottom: 30, left: 40}
    var width = +svg.attr("width") - margin.left - margin.right
    var height = +svg.attr("height") - margin.top - margin.bottom
    var g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Setup the bar chart
    var x0 = d3.scaleBand()
        .rangeRound([0, width])
        .paddingInner(0.1);
    var x1 = d3.scaleBand()
        .padding(0.05);
    var y = d3.scaleLinear()
        .rangeRound([height, 0]);
    var colorScale = d3.scaleOrdinal(fields.map(field => field["Color"]));
    var keys = fields.map(f => f['Label'])
    var chart = g.append("g")
    var axisBottom = g.append("g")
    var axisLeft = g.append("g")
    var titleChart = g.append("text")
    var yAxisLabel = g.append("text")
    var categoryLabel = chart.append("text")


    axisBottom
        .attr("class", "axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x0))

    var yName = d3.scaleBand()
        .domain(categories)
        .range([15, width - 60])
    g.append("g")
        .style("font-size", "14px")
        .attr("transform", "translate(20," + (height+10) + ")")
        .call(d3.axisBottom(yName).tickSize(0))
        .select(".domain").remove()

    axisLeft
        .attr("class", "axis")
        .call(d3.axisLeft(y).ticks(null, "s"));

    titleChart
        .attr("x", (width / 2))
        .attr("y", -5 - (margin.top / 2))
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .style("font-family", "Helvetica")
        .style("font-weight", "900")
        .text("Amount of agents per exit")

    yAxisLabel
        .attr("y", -30)
        .attr("text-anchor", "end")
        .attr("transform", "rotate(-90)")
        .text("Number of agents");

    //Render step
    this.render = function(data){
        //Axes
        var minY = d3.min(data, function(d){
            return d3.min(keys, function(key){
                return d[key];
            })
        })
        if(minY > 0){
            minY = 0;
        }
        var maxY = d3.max(data, function(d){
            return d3.max(keys, function(key){
                return d[key];
            })
        })

        x0.domain(data.map(function(d, i) { return i }));
        x1.domain(keys).rangeRound([0, x0.bandwidth()]);
        y.domain([minY,maxY]).nice();

        if(data.length > 1){
            axisBottom
                .attr("transform", "translate(0," + y(0) + ")")
                .call(d3.axisBottom(x0))
        }

        axisLeft.call(d3.axisLeft(y).ticks(null, "s"))

        //Sorting
        if(sorting != "none"){
            if(sorting == "ascending"){
                data.sort((a, b) => b[sortingKey] - a[sortingKey]);
            } else if (sorting == "descending") {
                data.sort((a, b) => a[sortingKey] - b[sortingKey]);
            }
        }

        //Draw Chart
        var rects = chart
            .selectAll("g")
            .data(data)
            .enter()
                .append("g")
                    .attr("transform", function(d, i) { return "translate(" + x0(i) + ",0)"; })

        //  add a rectangle to the chart
        rects.selectAll("rect")
            .data(function(d) {
                return keys.map(function(key) {
                    return {key: key, value: d[key]};
                });
            })
            .enter()
                .append("g")
                    .append("rect")
                        .attr("x", function(d) { return x1(d.key); })
                        .attr("width", x1.bandwidth())
                        .attr("fill", function(d) { return colorScale(d.key); })
                        .attr("y", function(d) { return Math.min(y(d.value),y(0)); })
                        .attr("height", function(d) { return Math.abs(y(d.value) - y(0)); })
                        .attr("stroke", "black")
                        .style("stroke-width", 2)

         //  add quantity label to each rectangle
        rects.selectAll("g")
	         .append("text")
	            .attr("x", function(d) { return x1(d.key)  + x1.bandwidth()/2 })
	            .attr("y", function(d) { return Math.min(y(d.value),y(0))-5; })
	            .style("font-weight", "900")
	            .text(function (d) { return d.value; })



        //Update chart rectangles
        chart
            .selectAll("g")
            .data(data)
            .selectAll("rect")
            .data(function(d) {
                return keys.map(function(key) {
                    return {key: key, value: d[key]};
                });
            })
            .attr("y", function(d) { return Math.min(y(d.value),y(0)); })
            .attr("height", function(d) { return Math.abs(y(d.value) - y(0)); })

         //Update chart quantity labels
        chart
            .selectAll("g")
            .data(data)
            .selectAll("text")
            .data(function(d) {
                return keys.map(function(key) {
                    return {key: key, value: d[key]};
                });
            })
            .attr("x", function(d) { return x1(d.key) + x1.bandwidth()/2; })
            .attr("y", function(d) { return Math.min(y(d.value),y(0))- 5; })
            .style("font-weight", "900")
            .text(function (d) { return d.value; })
    }

    this.reset = function(){
        chart.selectAll("g")
            .data([])
            .exit().remove();
    }

}
