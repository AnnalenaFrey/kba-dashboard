import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

function useBrands(){
  return useQuery<string[]>({
    queryKey: ["brands"],
    queryFn: () =>
      fetch("http://127.0.0.1:8000/analytics/brands").then((res) => res.json()
    ),
  });
}

function useSegments(){
  return useQuery<string[]>({
    queryKey: ["segments"],
    queryFn: () =>
      fetch("http://127.0.0.1:8000/analytics/segments").then((res) => res.json()
    ),
  });
}

function useTimeSeries(segment: string, brand: string){
  const params = new URLSearchParams();
  
  if (segment !== "") params.append("segment", segment);
  if (brand !== "") params.append("brand", brand)

  return useQuery<string[]>({
    queryKey: ["timeseries", segment, brand],
    queryFn: () =>
      fetch(`http://127.0.0.1:8000/analytics/timeseries/?${params.toString()}`).then((res) => res.json()
      ),
  });
}

function SegmentDropdown({ segments, currentSegment, setSelectedSegment }){
  return(
    <select
      value = {currentSegment}
      onChange={e => setSelectedSegment(e.target.value)}
    >
      <option value="">ALLE SEGMENTE</option>
      {segments.map((segment) => (
        <option key={segment} value={segment}>{segment}</option>
      ))}
    </select>
  );
}

function BrandDropdown({ brands, currentBrand, setSelectedBrand }){
  return(
    <select
      value = {currentBrand}
      onChange={e => setSelectedBrand(e.target.value)}
    >
      <option value="">ALLE MARKEN</option>
      {brands.map((brand) => (
        <option key={brand} value={brand}>{brand}</option>
      ))}
    </select>
  );
}


export default function App() {
  const brands = useBrands();
  const segments = useSegments();
  const [currentSegment, setSelectedSegment] = useState<string>("");
  const [currentBrand, setSelectedBrand] = useState<string>("");
  const timeSeries = useTimeSeries(currentSegment, currentBrand)

  if (brands.isPending || segments.isPending || timeSeries.isPending) return <div>Loading ...</div>;
  if (brands.isError || segments.isError || timeSeries.isError) return <div>Something went wrong... </div>;

  return(
    <div>
      <SegmentDropdown
        segments={segments.data}
        currentSegment={currentSegment}
        setSelectedSegment={setSelectedSegment}
      />
      <BrandDropdown
        brands={brands.data}
        currentBrand={currentBrand}
        setSelectedBrand={setSelectedBrand}
      />
      <ul>
        {timeSeries.data.map((entry) => (
          <li key={`${entry.year}-${entry.month}`}>
            {entry.year}-{entry.month}: {entry.segment} {entry.brand} {entry.total_car_registrations}
          </li>
        ))}
      </ul>
    </div>
  );
}