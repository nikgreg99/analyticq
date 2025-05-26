import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { deleteScanById } from "services/scanService";
import { toaster } from "../components/ui/general/Toaster";

export const useDeleteScan = (scanData) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const navigate = useNavigate();

  const handleDelete = useCallback(async () => {
    try {
      setIsDeleting(true);
      await deleteScanById(scanData.id);
      toaster.create({
        title: "Scan deleted successfully",
        type: "success",
        placement: "top-end",
      });
      navigate(`/contexts/${scanData.context_id}`);
    } catch (error) {
      toaster.create({
        title: "Failed to delete scan",
        description: error.message,
        type: "error",
        placement: "top-end",
      });
    } finally {
      setIsDeleting(false);
      setIsDialogOpen(false);
    }
  }, [scanData, navigate]);

  return {
    isDeleting,
    isDialogOpen,
    setIsDialogOpen,
    handleDelete,
  };
};
