var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 270 - margin.top - margin.bottom;

var x = d3.scale.linear()
    .domain([0, 60])
    .range([0, width]);

var x_axis_scale = d3.scale.linear()
    .domain([0, 180])
    .range([0, width]);

var y = d3.scale.linear()
    .domain([0, 32])
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x_axis_scale)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var line = d3.svg.line()
    .x(function(d) { return x(d.pos); })
    .y(function(d) { return y(d.count); });

var svg = d3.select("#graph").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var count_list = [];

function circle_transform(item) {
  var scaled_pos = x(item.pos);
  var scaled_cnt = y(item.count);
  return "translate(" + scaled_pos + "," + scaled_cnt + ")";
}

function get_count() {
  var data = [];

  count_list.forEach(function (item, idx, arr) {
      var p = Object();
      p.pos = idx;
      p.count = +item.count;
      p.total_count = +item.total_count;
      p.packet_id = item.packet_id;
      p.packet_ids = item.packet_ids;
      p.errors = item.errors;
      data.push(p);
  });

  return data;
}

function packet_click(packet) {
  if (packet.packet_ids.length == 0) {
    return;
  }

  var countline = d3.select("#packets");
  countline.selectAll('p').remove();
  packet.packet_ids.forEach(function (item) {
    d3.json("/count-packets/" + item, function(error, data) {
        if (error) throw error;
        data['count-packet'].logs.forEach(function (item) {
            countline.append('p')
                .attr("class", "packet-log-line")
                .text(item);
        });
    });
  });
}

function initialize() {
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
    .append("text")
      .attr("y", 6)
      .attr("dy", "2.25em")
      .text("seconds");

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("logs lines");

  svg.append("g")
      .attr("id", "countline");
}

function get_bar_class(data) {
  if (data.errors == true) {
    return "bar-errors";
  }
  return "bar";
}

function update() {
  var data = get_count();
  d3.select("#countline").selectAll("rect").remove();
  data.forEach(function (item) {
    d3.select("#countline")
        .append("rect")
          .datum(item)
          .attr("class", get_bar_class)
          .attr("x", function (d) { return x(d.pos); })
          .attr("width", width/60)
          .attr("y", function (d) { return y(d.total_count); })
          .attr("height", function (d) { return height - y(d.total_count); })
          .on("click", packet_click);
  });
}

function update_line_and_circles() {
  var data = get_count();
  d3.select("#countline").selectAll("path").remove();
  d3.select("#countline").append("path")
        .datum(data)
        .attr("class", "line")
        .attr("d", line);
  data.forEach(function (item) {
    d3.select("#countline").append("path")
          .datum(item)
          .attr("transform", circle_transform(item))
          .attr("class", "circle")
          .attr("d", d3.svg.symbol().size(40))
          .on("click", packet_click);
  });
}

initialize();

setInterval(function() {
  d3.json("/count-packets", function(error, data) {
      if (error) throw error;

      var p = Object();
      p.count = data["count-packets"]["last-received"].count;
      p.packet_id = data["count-packets"]["last-received"].id;
      p.total_count = data["count-packets"]["since-last-get"].count;
      p.packet_ids = data["count-packets"]["since-last-get"].ids;
      p.errors = data["count-packets"]["since-last-get"].errors;

      count_list.unshift(p);
      if (count_list.length >= 60) {
        count_list.pop();
      }

      update();
  });
}, 3000);
