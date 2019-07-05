module tide_module
    implicit none

    logical, save :: setup = .false.

    contains

    subroutine setup_tide()
        integer :: iunit
        integer, intent(out) :: wl_size
        real(kind=8), dimension (:,:), allocatable :: data_array
        real(kind=8), dimension (:), allocatable, intent(out) :: time_input, water_level
        real(kind=8) :: tmp

        if (.not. setup) then

            iunit = 10
            call getenv("WL_INPUT", wl_input)
            open(iunit, file=trim(adjustl(wl_input)), status='old', iostat=istat)
            if (istat /= 0) then
                print *, "Error opening water level data file. status = ", istat
                stop
            endif

            rewind(iunit)
            wl_size = 0
            do
                read(iunit, *, iostat=istat) tmp
                if (is_iostat_end(istat)) exit
                wl_size = wl_size + 1
            end do

            allocate(data_array(wl_size, 2))
            allocate(time_input(wl_size))
            allocate(water_level(wl_size))

            rewind(iunit)
            do i= 1, wl_size
                read(iunit, *, iostat=istat) data_array(i,:)
            end do

            close(unit=iunit, iostat=istat)

            time_input(:) = data_array(:,1)
            water_level(:) = data_array(:,2)

            deallocate(data_array)

            setup = .true.
        end if

    end subroutine setup_tide

end module tide_module
