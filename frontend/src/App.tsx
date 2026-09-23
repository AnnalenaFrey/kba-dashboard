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

function SegmentDropdown({ segments, currentSegment, setSelectedSegment }){
  return(
    <select
      value = {currentSegment}
      onChange={e => setSelectedSegment(e.target.value)}
    >
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
      {brands.map((brand) => (
        <option key={brand} value={brand}>{brand}</option>
      ))}
    </select>
  );
}


export default function App() {
  const brands = useBrands();
  const segments = useSegments();
  const [currentSegment, setSelectedSegment] = useState("");
  const [currentBrand, setSelectedBrand] = useState("");


  if (brands.isPending || segments.isPending) return <div>Loading ...</div>;
  if (brands.isError || segments.isError) return <div>Something went wrong... </div>;

  return(
    <div>
      <BrandDropdown
        brands={brands.data}
        currentBrand={currentBrand}
        setSelectedBrand={setSelectedBrand}
      />
      <SegmentDropdown
        segments={segments.data}
        currentSegment={currentSegment}
        setSelectedSegment={setSelectedSegment}
      />
    </div>
  );
}