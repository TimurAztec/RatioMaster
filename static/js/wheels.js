$(document).ready(() => {
    let wheelSizes = [
        { label: "700x23 (622-23)", value: 2105 },
        { label: "700x25 (622-25)", value: 2110 },
        { label: "700x28 (622-28)", value: 2136 },
        { label: "700x32 (622-32)", value: 2155 },
        { label: "700x35 (622-35)", value: 2168 },
        { label: "700x38 (622-38)", value: 2180 },
        { label: "700x40 (622-40)", value: 2200 },
        { label: "700x42 (622-42)", value: 2224 },
        { label: "700x45 (622-45)", value: 2242 },
        { label: "700x50 (622-50)", value: 2270 },
        { label: "26x1.0 (559-25)", value: 1913 },
        { label: "26x1.5 (559-40)", value: 1948 },
        { label: "26x1.75 (559-47)", value: 2026 },
        { label: "26x2.0 (559-50)", value: 2050 },
        { label: "26x2.1 (559-54)", value: 2068 },
        { label: "26x2.2 (559-56)", value: 2075 },
        { label: "27.5x1.5 (584-40)", value: 2079 },
        { label: "27.5x2.0 (584-50)", value: 2120 },
        { label: "27.5x2.1 (584-54)", value: 2148 },
        { label: "27.5x2.2 (584-56)", value: 2170 },
        { label: "29x1.9 (622-48)", value: 2250 },
        { label: "29x2.0 (622-50)", value: 2272 },
        { label: "29x2.1 (622-54)", value: 2288 },
        { label: "29x2.2 (622-56)", value: 2298 },
        { label: "29x2.25 (622-57)", value: 2305 },
        { label: "29x2.3 (622-58)", value: 2326 },
        { label: "29x2.4 (622-60)", value: 2345 },
        { label: "29x2.5 (622-62)", value: 2360 },
        { label: "29x2.6 (622-65)", value: 2380 },
        { label: "650x23B (571-23)", value: 1948 },
        { label: "650x25B (571-25)", value: 1952 },
        { label: "650x28B (571-28)", value: 1968 },
        { label: "650x42B (584-42)", value: 2100 },
        { label: "24x1.75 (507-47)", value: 1890 },
        { label: "24x2.0 (507-50)", value: 1925 },
        { label: "24x2.1 (507-54)", value: 1940 },
        { label: "20x1.75 (406-47)", value: 1590 },
        { label: "20x2.0 (406-50)", value: 1620 },
        { label: "20x2.1 (406-54)", value: 1640 },
        { label: "16x1.75 (305-47)", value: 1255 },
        { label: "16x2.0 (305-50)", value: 1275 },
        { label: "16x2.125 (305-54)", value: 1290 }
    ];

    $.each(wheelSizes, (index, size) => {
        let option = $('<option></option>').val(size.value).text(size.label);
        $('#t').append(option);
    });
});