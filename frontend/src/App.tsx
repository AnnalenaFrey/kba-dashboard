import { useQuery } from "@tanstack/react-query";

function useBrands(){
  const { isPending, error, data } = useQuery({
    queryKey: ["brands"],
    queryFn: () =>
      fetch("http://127.0.0.1:8000/analytics/brands").then((res) => res.json()
    ),
  });

  if (isPending) return "Loading...";
  if (error) return "An error has occurd: " + error.message;

  return data;
}

function useSegments(){
  const { isPending, error, data } = useQuery({
    queryKey: ["segments"],
    queryFn: () =>
      fetch("http://127.0.0.1:8000/analytics/segments").then((res) => res.json()
    ),
  });

  if (isPending) return "Loading...";
  if (error) return "An error has occurd: " + error.message;

  return data;
}


export default function App() {
  const brands = useBrands();
  const segments = useSegments();

  return(
    <div>
      { brands }
      { segments }
    </div>
  );
}